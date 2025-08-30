"""Unit tests for JupyterPlugin.set_base_model method with ModelSessionService."""

from unittest.mock import Mock

import pytest

from mais.application.services.model_session_service import ModelSessionService
from mais.domain.model_analysis.value_objects.model_metadata import (
    ModelMetadata,
)
from mais.presentation.jupyter.mais_plugin import JupyterPlugin


class TestJupyterPluginSetBaseModel:
    """Test JupyterPlugin.set_base_model method with ModelSessionService."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create mock dependencies
        self.mock_model_analysis_service = Mock()
        self.mock_model_session_service = Mock(spec=ModelSessionService)

        # Create plugin instance
        self.plugin = JupyterPlugin(
            model_analysis_service=self.mock_model_analysis_service,
            model_session_service=self.mock_model_session_service,
            api_token="test-token",
            api_uri="https://test.api",
        )

    def test_set_base_model_with_valid_key(self):
        """Test set_base_model with a valid model key."""
        # Setup loaded models
        model1 = ModelMetadata(
            name="model1", supplier="supplier1", version="1.0"
        )
        model2 = ModelMetadata(
            name="model2", supplier="supplier2", version="2.0"
        )

        self.mock_model_session_service.list_detected_models.return_value = {
            "supplier1/model1": model1,
            "supplier2/model2": model2,
        }

        # Call set_base_model
        self.plugin.set_base_model("supplier1/model1")

        # Verify base model is set correctly
        assert self.plugin._base_model == model1

    def test_set_base_model_with_invalid_key(self):
        """Test set_base_model with an invalid model key falls back to latest."""
        # Setup loaded models
        model1 = ModelMetadata(name="model1", supplier="supplier1")
        model2 = ModelMetadata(name="model2", supplier="supplier2")

        self.mock_model_session_service.list_detected_models.return_value = {
            "key1": model1,
            "key2": model2,
        }

        # Call set_base_model with invalid key
        self.plugin.set_base_model("invalid/key")

        # Verify fallback to latest model (model2)
        assert self.plugin._base_model == model2

    def test_set_base_model_with_none_key(self):
        """Test set_base_model with None key defaults to latest."""
        # Setup loaded models
        model1 = ModelMetadata(name="model1")
        model2 = ModelMetadata(name="model2")
        model3 = ModelMetadata(name="model3")

        self.mock_model_session_service.list_detected_models.return_value = {
            "model1": model1,
            "model2": model2,
            "model3": model3,
        }

        # Call set_base_model with None
        self.plugin.set_base_model(None)

        # Verify defaults to latest model (model3)
        assert self.plugin._base_model == model3

    def test_set_base_model_with_empty_loaded_models(self):
        """Test set_base_model raises ValueError when no models are loaded."""
        # Setup empty loaded models
        self.mock_model_session_service.list_detected_models.return_value = {}

        # Call set_base_model and expect ValueError
        with pytest.raises(
            ValueError, match="No models loaded in the repository"
        ):
            self.plugin.set_base_model("any-key")

    def test_set_base_model_preserves_order(self):
        """Test that set_base_model correctly uses the last model when defaulting."""
        # Setup loaded models with specific order
        models = {}
        for i in range(10):
            model = ModelMetadata(name=f"model{i}", version=f"{i}.0")
            models[f"key{i}"] = model

        self.mock_model_session_service.list_detected_models.return_value = (
            models
        )

        # Call set_base_model with invalid key to trigger default
        self.plugin.set_base_model("invalid")

        # Should default to the last model (model9)
        expected_model = ModelMetadata(name="model9", version="9.0")
        assert self.plugin._base_model.name == expected_model.name
        assert self.plugin._base_model.version == expected_model.version

    def test_set_base_model_with_empty_string_key(self):
        """Test set_base_model with empty string key."""
        # Setup loaded models
        model1 = ModelMetadata(name="model1", supplier="supplier1")
        self.mock_model_session_service.list_detected_models.return_value = {
            "supplier1/model1": model1
        }

        # Call set_base_model with empty string
        self.plugin.set_base_model("")

        # Verify it defaults to latest model
        assert self.plugin._base_model == model1

    def test_set_base_model_case_sensitivity(self):
        """Test that set_base_model is case-sensitive for keys."""
        # Setup loaded models
        model1 = ModelMetadata(name="model1", supplier="Supplier1")
        self.mock_model_session_service.list_detected_models.return_value = {
            "Supplier1/model1": model1
        }

        # Call with different case
        self.plugin.set_base_model("supplier1/model1")  # lowercase

        # Should default to latest since key doesn't match
        assert self.plugin._base_model == model1

    def test_set_base_model_updates_internal_state(self):
        """Test that set_base_model properly updates internal state."""
        # Setup loaded models
        model1 = ModelMetadata(name="model1")
        model2 = ModelMetadata(name="model2")

        models_dict = {"key1": model1, "key2": model2}
        self.mock_model_session_service.list_detected_models.return_value = (
            models_dict
        )

        # Initially no base model
        assert (
            not hasattr(self.plugin, "_base_model")
            or self.plugin._base_model is None
        )

        # Set first base model
        self.plugin.set_base_model("key1")
        assert self.plugin._base_model == model1

        # Change base model
        self.plugin.set_base_model("key2")
        assert self.plugin._base_model == model2

        # Invalid key should still update to latest
        self.plugin.set_base_model("invalid")
        assert self.plugin._base_model == model2  # Latest

    def test_set_base_model_with_complex_metadata(self):
        """Test set_base_model with complex ModelMetadata objects."""
        # Create complex model metadata
        model_data = ModelMetadata(
            name="gpt-4-turbo",
            supplier="OpenAI",
            version="2024.01.15",
            supplier_country="United States",
        )

        # Add to loaded models
        self.mock_model_session_service.list_detected_models.return_value = {
            "OpenAI/gpt-4-turbo": model_data
        }

        # Set base model
        self.plugin.set_base_model("OpenAI/gpt-4-turbo")

        # Verify all properties are accessible
        assert self.plugin._base_model.name == "gpt-4-turbo"
        assert self.plugin._base_model.supplier == "OpenAI"
        assert self.plugin._base_model.version == "2024.01.15"
        assert self.plugin._base_model.supplier_country == "United States"

    def test_set_base_model_multiple_calls(self):
        """Test multiple calls to set_base_model."""
        # Setup multiple models
        models = {}
        for i in range(5):
            model = ModelMetadata(name=f"model{i}", version=f"{i}.0")
            models[f"key{i}"] = model

        self.mock_model_session_service.list_detected_models.return_value = (
            models
        )

        # Make multiple calls
        for i in range(5):
            self.plugin.set_base_model(f"key{i}")
            expected_model = models[f"key{i}"]
            assert self.plugin._base_model == expected_model

    def test_set_base_model_with_none_values_in_metadata(self):
        """Test set_base_model with ModelMetadata containing None values."""
        # Create metadata with None values
        model = ModelMetadata(name="model", supplier=None, version=None)

        self.mock_model_session_service.list_detected_models.return_value = {
            "model": model
        }

        # Set base model
        self.plugin.set_base_model("model")

        # Verify it works with None values
        assert self.plugin._base_model == model
        assert self.plugin._base_model.name == "model"
        assert self.plugin._base_model.supplier is None
        assert self.plugin._base_model.version is None


class TestModelSessionService:
    """Test ModelSessionService functionality."""

    def test_add_and_get_detected_model(self):
        """Test adding and retrieving detected models."""
        service = ModelSessionService()

        # Initially empty
        assert service.list_detected_models() == {}

        # Add a model
        model1 = ModelMetadata(name="bert", supplier="Google")
        service.add_detected_model("google/bert", model1)

        # Retrieve it
        assert service.get_detected_model("google/bert") == model1
        assert service.get_detected_model("nonexistent") is None

        # List should contain the model
        models = service.list_detected_models()
        assert len(models) == 1
        assert models["google/bert"] == model1

    def test_add_multiple_models(self):
        """Test adding multiple models to the service."""
        service = ModelSessionService()

        # Add multiple models
        model1 = ModelMetadata(name="gpt-3", supplier="OpenAI")
        model2 = ModelMetadata(name="claude", supplier="Anthropic")
        model3 = ModelMetadata(name="llama", supplier="Meta")

        service.add_detected_model("openai/gpt-3", model1)
        service.add_detected_model("anthropic/claude", model2)
        service.add_detected_model("meta/llama", model3)

        # Verify all models are stored
        models = service.list_detected_models()
        assert len(models) == 3
        assert models["openai/gpt-3"] == model1
        assert models["anthropic/claude"] == model2
        assert models["meta/llama"] == model3

    def test_overwrite_existing_model(self):
        """Test that adding a model with existing key overwrites it."""
        service = ModelSessionService()

        # Add initial model
        model1 = ModelMetadata(name="bert", version="1.0")
        service.add_detected_model("key1", model1)

        # Overwrite with new model
        model2 = ModelMetadata(name="bert", version="2.0")
        service.add_detected_model("key1", model2)

        # Should have the new model
        assert service.get_detected_model("key1") == model2
        assert service.get_detected_model("key1").version == "2.0"

    def test_list_detected_models_returns_copy(self):
        """Test that list_detected_models returns a copy, not the original dict."""
        service = ModelSessionService()

        # Add a model
        model = ModelMetadata(name="test")
        service.add_detected_model("key", model)

        # Get the list
        models = service.list_detected_models()

        # Modify the returned dict
        models["new_key"] = ModelMetadata(name="new")

        # Original should be unchanged
        assert len(service.list_detected_models()) == 1
        assert "new_key" not in service.list_detected_models()
