from mais.domain.model_analysis.value_objects.model_metadata import (
    ModelMetadata,
)


class ModelSessionService:
    """Service for managing detected models during a session."""

    def __init__(self):
        self.detected_models: dict[str, ModelMetadata] = {}

    def add_detected_model(
        self, key: str, model_metadata: ModelMetadata
    ) -> None:
        """Store a detected model for later reference."""
        self.detected_models[key] = model_metadata

    def get_detected_model(self, key: str) -> ModelMetadata | None:
        """Retrieve a detected model by key."""
        return self.detected_models.get(key)

    def list_detected_models(self) -> dict[str, ModelMetadata]:
        """Get all detected models."""
        return self.detected_models.copy()
