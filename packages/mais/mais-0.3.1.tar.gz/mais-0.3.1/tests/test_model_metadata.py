"""Unit tests for ModelMetadata value object."""

from pydantic import ValidationError
import pytest

from mais.domain.model_analysis.value_objects.model_metadata import (
    ModelMetadata,
)


class TestModelMetadata:
    """Test ModelMetadata value object."""

    def test_create_model_metadata_all_fields(self):
        """Test creating ModelMetadata with all fields."""
        metadata = ModelMetadata(
            name="gpt-4",
            supplier="OpenAI",
            version="1.0.0",
            supplier_country="USA",
        )

        assert metadata.name == "gpt-4"
        assert metadata.supplier == "OpenAI"
        assert metadata.version == "1.0.0"
        assert metadata.supplier_country == "USA"

    def test_create_model_metadata_minimal(self):
        """Test creating ModelMetadata with minimal fields."""
        metadata = ModelMetadata(name="bert")

        assert metadata.name == "bert"
        assert metadata.supplier is None
        assert metadata.version is None
        assert metadata.supplier_country is None

    def test_create_model_metadata_all_none(self):
        """Test creating ModelMetadata with all None values."""
        metadata = ModelMetadata()

        assert metadata.name is None
        assert metadata.supplier is None
        assert metadata.version is None
        assert metadata.supplier_country is None

    def test_model_metadata_from_dict(self):
        """Test creating ModelMetadata from dictionary."""
        data = {
            "name": "llama-2",
            "supplier": "Meta",
            "version": "2.0",
            "supplier_country": "USA",
        }
        metadata = ModelMetadata.from_dict(data)

        assert metadata.name == "llama-2"
        assert metadata.supplier == "Meta"
        assert metadata.version == "2.0"
        assert metadata.supplier_country == "USA"

    def test_model_metadata_from_dict_partial(self):
        """Test creating ModelMetadata from partial dictionary."""
        data = {"name": "claude", "supplier": "Anthropic"}
        metadata = ModelMetadata.from_dict(data)

        assert metadata.name == "claude"
        assert metadata.supplier == "Anthropic"
        assert metadata.version is None
        assert metadata.supplier_country is None

    def test_model_metadata_from_dict_empty(self):
        """Test creating ModelMetadata from empty dictionary."""
        metadata = ModelMetadata.from_dict({})

        assert metadata.name is None
        assert metadata.supplier is None
        assert metadata.version is None
        assert metadata.supplier_country is None

    def test_model_metadata_from_dict_extra_fields(self):
        """Test that from_dict ignores extra fields."""
        data = {
            "name": "model",
            "supplier": "company",
            "extra_field": "ignored",
            "another_field": 123,
        }
        metadata = ModelMetadata.from_dict(data)

        assert metadata.name == "model"
        assert metadata.supplier == "company"
        assert not hasattr(metadata, "extra_field")
        assert not hasattr(metadata, "another_field")

    def test_model_metadata_to_dict(self):
        """Test converting ModelMetadata to dictionary."""
        metadata = ModelMetadata(
            name="gpt-4",
            supplier="OpenAI",
            version="1.0.0",
            supplier_country="USA",
        )

        result = metadata.to_dict()
        expected = {
            "name": "gpt-4",
            "supplier": "OpenAI",
            "version": "1.0.0",
            "supplier_country": "USA",
        }
        assert result == expected

    def test_model_metadata_to_dict_excludes_none(self):
        """Test that to_dict excludes None values."""
        metadata = ModelMetadata(name="bert", supplier="Google")

        result = metadata.to_dict()
        expected = {"name": "bert", "supplier": "Google"}
        assert result == expected
        assert "version" not in result
        assert "supplier_country" not in result

    def test_model_metadata_str_representation(self):
        """Test string representation of ModelMetadata."""
        # Test with all fields
        metadata = ModelMetadata(
            name="gpt-4",
            supplier="OpenAI",
            version="1.0.0",
            supplier_country="USA",
        )
        assert str(metadata) == "OpenAI/gpt-4/v1.0.0"

        # Test with supplier and name only
        metadata = ModelMetadata(name="bert", supplier="Google")
        assert str(metadata) == "Google/bert"

        # Test with name only
        metadata = ModelMetadata(name="model")
        assert str(metadata) == "model"

        # Test with supplier only
        metadata = ModelMetadata(supplier="Company")
        assert str(metadata) == "Company"

        # Test with all None
        metadata = ModelMetadata()
        assert str(metadata) == "Unknown Model"

    def test_model_metadata_immutability(self):
        """Test that ModelMetadata is immutable due to frozen config."""
        metadata = ModelMetadata(name="gpt-4", supplier="OpenAI")

        # Attempting to modify should raise an error
        with pytest.raises(ValidationError):
            metadata.name = "new-name"

        with pytest.raises(ValidationError):
            metadata.supplier = "new-supplier"

        with pytest.raises(ValidationError):
            metadata.version = "new-version"

    def test_model_metadata_equality(self):
        """Test equality comparison of ModelMetadata."""
        metadata1 = ModelMetadata(
            name="gpt-4", supplier="OpenAI", version="1.0"
        )
        metadata2 = ModelMetadata(
            name="gpt-4", supplier="OpenAI", version="1.0"
        )
        metadata3 = ModelMetadata(
            name="gpt-3", supplier="OpenAI", version="1.0"
        )

        assert metadata1 == metadata2
        assert metadata1 != metadata3
        assert metadata1 != "not a metadata object"

    def test_model_metadata_hash(self):
        """Test that ModelMetadata is hashable."""
        metadata1 = ModelMetadata(name="gpt-4", supplier="OpenAI")
        metadata2 = ModelMetadata(name="gpt-4", supplier="OpenAI")
        metadata3 = ModelMetadata(name="bert", supplier="Google")

        # Same data should have same hash
        assert hash(metadata1) == hash(metadata2)

        # Can be used in sets
        metadata_set = {metadata1, metadata2, metadata3}
        assert len(metadata_set) == 2  # metadata1 and metadata2 are equal

    def test_model_metadata_type_validation(self):
        """Test that ModelMetadata validates field types."""
        # String fields should accept strings
        metadata = ModelMetadata(
            name="model",
            supplier="company",
            version="1.0",
            supplier_country="USA",
        )
        assert all(
            isinstance(v, str | type(None))
            for v in [
                metadata.name,
                metadata.supplier,
                metadata.version,
                metadata.supplier_country,
            ]
        )

    def test_model_metadata_edge_cases(self):
        """Test edge cases for ModelMetadata."""
        # Empty strings are allowed
        metadata = ModelMetadata(
            name="", supplier="", version="", supplier_country=""
        )
        assert metadata.name == ""
        assert metadata.supplier == ""
        assert metadata.version == ""
        assert metadata.supplier_country == ""
        # Empty strings are treated as falsy, so returns "Unknown Model"
        assert str(metadata) == "Unknown Model"

        # Whitespace strings are preserved
        metadata = ModelMetadata(name="  ", supplier="  ")
        assert metadata.name == "  "
        assert metadata.supplier == "  "

        # Special characters are preserved
        metadata = ModelMetadata(
            name="model/with/slashes",
            supplier="company@2024",
            version="1.0-beta",
        )
        assert metadata.name == "model/with/slashes"
        assert metadata.supplier == "company@2024"
        assert metadata.version == "1.0-beta"
