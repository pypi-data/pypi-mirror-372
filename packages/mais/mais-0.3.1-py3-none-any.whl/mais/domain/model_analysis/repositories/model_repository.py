"""Repository interface for model data."""

from abc import ABC, abstractmethod
from typing import Any

from mais.domain.model_analysis.value_objects import ModelID
from mais.domain.model_analysis.value_objects.model_metadata import (
    ModelMetadata,
)


class ModelRepository(ABC):
    """Abstract repository for accessing model data."""

    @abstractmethod
    def find_by_id(self, model_id: ModelID) -> dict[str, Any] | None:
        """Find model data by ID.

        Args:
            model_id: The model identifier

        Returns:
            Model data if found, None otherwise
        """
        pass

    @abstractmethod
    def exists(self, model_id: ModelID) -> bool:
        """Check if a model exists in the repository.

        Args:
            model_id: The model identifier

        Returns:
            True if model exists
        """
        pass

    @abstractmethod
    def is_approved(self, model_id: ModelID) -> bool:
        """Check if a model is approved for use.

        Args:
            model_id: The model identifier

        Returns:
            True if model is approved
        """
        pass

    @abstractmethod
    def trigger_quickscan_analysis(self, model_id: str) -> dict[str, Any]:
        """Trigger a quickscan analysis for a model.

        Args:
            model_id: The model identifier

        Returns:
            Quickscan results as a string, or None if not available
        """
        pass

    @abstractmethod
    def get_model_data_from_model_analysis(
        self, model_id: str
    ) -> dict[str, Any] | None:
        """Get model data from model analysis.

        Args:
            model_id: The model identifier

        Returns:
            Model data if available, None otherwise
        """
        pass

    @abstractmethod
    def register_model(
        self,
        model_name: str,
        model_version: str,
        supplier: str,
        supplier_country: str,
        software_dependencies: list[Any],
        datasets: list[Any],
        base_model_data: ModelMetadata,
    ) -> ModelID:
        """Register a new model in the repository.

        Args:
            model_name: The name of the model
            model_version: The version of the model
            supplier: The supplier of the model
            supplier_country: The country of the supplier
            sofware_dependencies: List of software dependencies for the model
            datasets: List of datasets used by the model
            base_model_data: base model data if applicable
        Returns:
            The unique identifier for the registered model
        """
        pass
