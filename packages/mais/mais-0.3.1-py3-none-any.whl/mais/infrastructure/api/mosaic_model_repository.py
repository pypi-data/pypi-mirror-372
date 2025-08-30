"""MOSAIC API implementation of model repository."""

import json
from typing import Any

import requests

from mais.config import get_config
from mais.domain.exceptions import (
    ModelNotFoundError,
    MosaicAPIError,
    MosaicAuthenticationError,
    MosaicConnectionError,
)
from mais.domain.model_analysis.repositories import ModelRepository
from mais.domain.model_analysis.value_objects import ModelID
from mais.domain.model_analysis.value_objects.model_metadata import (
    ModelMetadata,
)
from mais.utils.logger import logger
from mais.utils.notebook import get_current_notebook_data


class MosaicModelRepository(ModelRepository):
    """MOSAIC API implementation of model repository."""

    def __init__(
        self,
        api_url: str | None = None,
        api_token: str | None = None,
        enabled: bool | None = None,
    ):
        """Initialize the MOSAIC repository.

        Args:
            api_url: MOSAIC API URL (overrides config)
            api_token: API authentication token (overrides config)
            enabled: Whether MOSAIC integration is enabled (overrides config)
        """
        config = get_config()
        self.api_url = api_url or config.mosaic_api_url
        self.api_token = api_token or config.manifest_api_token
        self.enabled = enabled if enabled is not None else config.mosaic_enabled
        self.api_timeout = config.api_timeout
        self.logger = logger
        self._quickscan_results: dict[str, dict[str, Any]] = {}

    def find_by_id(self, model_id: ModelID) -> dict[str, Any] | None:
        """Find model data by ID.

        Args:
            model_id: The model identifier

        Returns:
            Model data if found, None otherwise
        """
        if not self.enabled:
            return None

        try:
            return self._check_model_in_inventory(model_id)
        except (
            ModelNotFoundError,
            MosaicAPIError,
            MosaicConnectionError,
            MosaicAuthenticationError,
        ):
            return None

    def exists(self, model_id: ModelID) -> bool:
        """Check if a model exists in the repository.

        Args:
            model_id: The model identifier

        Returns:
            True if model exists
        """
        return self.find_by_id(model_id) is not None

    def is_approved(self, model_id: ModelID) -> bool:
        """Check if a model is approved for use.

        Args:
            model_id: The model identifier

        Returns:
            True if model is approved
        """
        if not self.enabled:
            return True  # Allow all models when disabled

        try:
            self._check_model_in_inventory(model_id)
            return True  # If no exception, model is approved
        except (
            ModelNotFoundError,
            MosaicAPIError,
            MosaicConnectionError,
            MosaicAuthenticationError,
        ):
            return False

    def check_connection(self) -> bool:
        """Check if the MOSAIC API is accessible.

        Returns:
            True if connection successful, False otherwise

        Note:
            This method logs exceptions internally but doesn't raise them,
            to maintain backward compatibility with boolean return type.
        """
        if not self.enabled:
            return False

        try:
            headers = {"Authorization": f"Bearer {self.api_token}"}
            response = requests.get(
                f"{self.api_url}/v1/health",
                headers=headers,
                timeout=self.api_timeout,
            )

            if response.status_code == 200:
                self.logger.debug("Successfully connected to MOSAIC API")
                return True
            elif response.status_code == 401:
                # Log authentication error but don't raise
                self.logger.error(
                    f"MOSAIC API authentication failed: {response.status_code} - {response.text}"
                )
                return False
            else:
                # Log API error but don't raise
                self.logger.warning(
                    f"Failed to connect to MOSAIC API: {response.status_code} - {response.text}"
                )
                return False

        except requests.exceptions.RequestException as e:
            # Log connection error but don't raise
            self.logger.warning(f"Error connecting to MOSAIC API: {e!s}")
            return False

    def validate_model(self, model_id: str) -> dict[str, Any]:
        """Validate a model and return its data if approved.

        Args:
            model_id: The model identifier to validate

        Returns:
            Model data dictionary

        Raises:
            ModelNotFoundError: If model is not in inventory
            MosaicAuthenticationError: If authentication fails
            MosaicAPIError: If API request fails
        """
        # Create ModelID value object
        model_id_obj = ModelID(model_id)
        return self._check_model_in_inventory(model_id_obj)

    def _check_model_in_inventory(self, model_id: ModelID) -> dict[str, Any]:
        """Internal method to check if a model exists in the approved inventory.

        Args:
            model_id: The model identifier to check

        Returns:
            Model data dictionary if found

        Raises:
            ModelNotFoundError: If model is not in inventory
            MosaicAuthenticationError: If authentication fails
            MosaicConnectionError: If connection fails
            MosaicAPIError: If API request fails
        """
        if not self.enabled:
            return {}  # Return empty dict when disabled

        # Use the model name for API lookup
        model_name = model_id.name

        endpoint = (
            f"{self.api_url}/v1/models/inventory?search={model_name}&limit=1"
        )
        headers = {"Authorization": f"Bearer {self.api_token}"}

        try:
            self.logger.debug(
                f"Checking if model '{model_id}' is in approved inventory..."
            )
            response = requests.get(
                endpoint, headers=headers, timeout=self.api_timeout
            )

            if response.status_code == 200:
                response_data = response.json()
                self.logger.debug(
                    f"Model inventory response data: {response_data}"
                )

                models = response_data.get("data", [])
                is_in_inventory = len(models) > 0

                if not is_in_inventory:
                    self.logger.debug(
                        f"Model '{model_id}' not found in inventory"
                    )
                    raise ModelNotFoundError(str(model_id))

                model_data = models[0] if models else {}
                self.logger.debug(f"Model '{model_id}' found in inventory")
                self.logger.debug(f"Model data: {model_data}")
                return model_data

            elif response.status_code == 401:
                # Handle authentication errors
                self.logger.error(
                    f"MOSAIC API authentication error: {response.text}"
                )
                raise MosaicAuthenticationError()

            elif response.status_code == 404:
                self.logger.debug(f"Model '{model_id}' not found in inventory")
                raise ModelNotFoundError(str(model_id))

            else:
                self.logger.warning(
                    f"MOSAIC API error: {response.status_code} - {response.text}"
                )
                raise MosaicAPIError(
                    "Unexpected response from API",
                    status_code=response.status_code,
                    response_text=response.text,
                )

        except requests.exceptions.RequestException as e:
            self.logger.warning(f"MOSAIC API request error: {e!s}")
            raise MosaicConnectionError(str(e)) from e

        except json.JSONDecodeError as e:
            self.logger.warning("MOSAIC API returned invalid JSON response")
            raise MosaicAPIError("Invalid JSON response from API") from e

    def trigger_quickscan_analysis(self, model_id: str) -> dict[str, Any]:
        """Fetch quickscan results for a model.

        Args:
            model_id: The model identifier

        Returns:
            Quickscan results dictionary

        Raises:
            MosaicAPIError: If API request fails
            MosaicConnectionError: If connection fails
        """
        if not self.enabled:
            return {}

        endpoint = (
            f"{self.api_url}/v1/model-analysis/quicksearch?query={model_id}"
        )
        headers = {"Authorization": f"Bearer {self.api_token}"}

        try:
            response = requests.get(
                endpoint, headers=headers, timeout=self.api_timeout
            )

            if response.status_code == 200:
                response_data = response.json()
                body_data = response_data.get("data", [])
                body = body_data[0] if body_data else {}
                # POST request to trigger quickscan analysis
                post_endpoint = f"{self.api_url}/v1/model-analysis"
                post_response = requests.post(
                    post_endpoint,
                    headers=headers,
                    json=body,
                    timeout=self.api_timeout,
                )
                if post_response.status_code == 200:
                    quickscan_results = post_response.json()
                    self.logger.debug(
                        f"Quickscan results for model '{model_id}': {quickscan_results}"
                    )
                    quickscan_results = {
                        "object_id": quickscan_results["data"]["_id"],
                    }
                    self.logger.debug(
                        f"Quickscan results for model '{model_id}': {quickscan_results}"
                    )
                    self._quickscan_results[model_id] = quickscan_results
                    return quickscan_results
                else:
                    self.logger.warning(
                        f"Failed to trigger quickscan: {post_response.status_code} - {post_response.text}"
                    )
                    raise MosaicAPIError(
                        "Failed to trigger quickscan",
                        status_code=post_response.status_code,
                        response_text=post_response.text,
                    )
            elif response.status_code == 401:
                self.logger.error(
                    f"MOSAIC API authentication error: {response.text}"
                )
                raise MosaicAuthenticationError()
            elif response.status_code == 404:
                self.logger.debug(
                    f"Quickscan results for model '{model_id}' not found"
                )
                raise ModelNotFoundError(str(model_id))
            else:
                self.logger.warning(
                    f"Failed to fetch quickscan results: {response.status_code} - {response.text}"
                )
                raise MosaicAPIError(
                    "Failed to fetch quickscan results",
                    status_code=response.status_code,
                    response_text=response.text,
                )

        except requests.exceptions.RequestException as e:
            self.logger.warning(f"Error fetching quickscan results: {e!s}")
            raise MosaicConnectionError(str(e)) from e

    def get_model_data_from_model_analysis(
        self, model_id: str
    ) -> dict[str, Any] | None:
        """Get model data from quickscan analysis.

        Args:
            model_id: The model identifier

        Returns:
            Model data if available, None otherwise
        """
        if not self.enabled:
            return None
        model_data: dict[str, Any] = {}
        RETRY_SECONDS = 5
        RETRY_MAX_ATTEMPTS = 5
        retries = 0
        is_analysis_finished = False
        model_metadata: ModelMetadata | None = None
        while not is_analysis_finished and retries < RETRY_MAX_ATTEMPTS:
            try:
                model_object_id = self._quickscan_results.get(model_id, {}).get(
                    "object_id"
                )
                self.logger.debug(
                    f"Fetching model data from quickscan for model '{model_id}' with object ID '{model_object_id}'"
                )
                endpoint = f"{self.api_url}/v1/model-analysis/{model_object_id}"
                headers = {"Authorization": f"Bearer {self.api_token}"}
                response = requests.get(
                    endpoint, headers=headers, timeout=self.api_timeout
                )
                if response.status_code == 200:
                    response_data = response.json()
                    model_data = response_data.get("data", {})
                    self.logger.debug(f"Model data: {model_data}")
                    if model_data:
                        model_metadata = ModelMetadata(
                            name=model_data.get("name", ""),
                            supplier=model_data.get("supplier", ""),
                            version=model_data.get("version", ""),
                            supplier_country=model_data.get(
                                "supplierCountry", ""
                            ),
                        )

                        risk_score = model_data.get("riskOverview", {}).get(
                            "riskScore", "Unknown"
                        )
                        self.logger.debug(
                            f"Risk score for model '{model_id}': {risk_score}"
                        )
                        findings = model_data.get("riskOverview", {}).get(
                            "findings", []
                        )
                        # get only findings with category 'needs_review'
                        if risk_score != "pending":
                            is_analysis_finished = True
                            findings = [
                                finding.get("description", "")
                                for finding in findings
                                if finding.get("category") == "needs_review"
                            ]
                            self.logger.debug(
                                f"Findings for model '{model_id}': {findings}"
                            )
                            model_risk_assessment_data = {
                                "risk_score": risk_score,
                                "findings": findings,
                                "model_metadata": model_metadata,
                            }
                            return model_risk_assessment_data
                        else:
                            self.logger.debug(
                                f"Risk score is pending for '{model_id}', retrying..."
                            )
                            # Wait before retrying
                            import time

                            time.sleep(RETRY_SECONDS)
                    else:
                        # Empty model data - analysis not complete, continue retrying
                        self.logger.debug(
                            f"No model data found for '{model_id}' in quickscan"
                        )
                        self.logger.debug(
                            f"Response Status Code: {response.status_code}"
                        )
                        self.logger.debug(
                            f"Retrying to fetch model data for '{model_id}' in {RETRY_SECONDS} seconds..."
                        )
                        # Wait before retrying
                        import time

                        time.sleep(RETRY_SECONDS)
                elif response.status_code == 404:
                    self.logger.debug(
                        f"Model data for '{model_id}' not found in quickscan"
                    )
                    return None
                else:
                    self.logger.warning(
                        f"Failed to fetch model data from quickscan: {response.status_code} - {response.text}"
                    )
                    raise MosaicAPIError(
                        "Failed to fetch model data from quickscan",
                        status_code=response.status_code,
                        response_text=response.text,
                    )
            except (MosaicAPIError, MosaicConnectionError, ModelNotFoundError):
                return None

            retries += 1

        if retries >= RETRY_MAX_ATTEMPTS and not is_analysis_finished:
            self.logger.warning(
                f"Max retries reached for fetching model data from quickscan for model '{model_id}'"
            )
            supplier, name = model_id.split("/", 1)
            # If analysis is still pending after retries, return default data
            model_risk_assessment_data = {
                "risk_score": "Unknown",
                "findings": [],
                "model_metadata": model_metadata
                or ModelMetadata(
                    name=name,
                    supplier=supplier,
                    version="",
                    supplier_country="",
                ),
            }
            return model_risk_assessment_data

        # This should never be reached, but satisfies mypy
        return None

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
        """Register model risk assessment.

        Args:
            model_name The model identifier
            model_data: Model data dictionary

        Returns:
            Model risk assessment object
        """
        endpoint = f"{self.api_url}/v1/model-analysis/custom"
        headers = {"Authorization": f"Bearer {self.api_token}"}
        if not base_model_data:
            self.logger.error(
                "At least a model should be loaded as base model for registration"
            )
            raise ValueError("Base model data is required for registration")
        base_model_purl = (
            f"pkg:huggingface/{base_model_data.supplier}/{base_model_data.name}"
        )
        base_model = f"{base_model_data.supplier}/{base_model_data.name}"
        current_notebook = get_current_notebook_data()
        self.logger.debug(f"Current notebook data: {current_notebook}")
        self.logger.debug(f"Software dependencies: {software_dependencies}")
        payload = {
            "name": model_name,
            "version": model_version,
            "supplier": supplier,
            "supplierCountry": supplier_country,
            "parentModelPurl": base_model_purl,
            "parentModel": base_model,
            "datasets": datasets,
            "softwareDependencies": software_dependencies,
            "files": [current_notebook],
        }
        try:
            self.logger.debug(f"Registering model with payload: {payload}")
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=self.api_timeout,
            )
            if response.status_code == 200:
                response_data = response.json()
                self.logger.debug(
                    f"Model registration response: {response_data}"
                )
                model_id = response_data.get("data", {}).get("_id")
                if model_id:
                    self.logger.debug(
                        f"Model '{model_id}' registered successfully"
                    )
                    return ModelID(model_id)
                else:
                    self.logger.error(
                        "Model registration failed: No model ID returned"
                    )
                    raise MosaicAPIError(
                        "Model registration failed: No model ID returned"
                    )
            else:
                self.logger.error(
                    f"Failed to register model: {response.status_code} - {response.text}"
                )
                raise MosaicAPIError(
                    "Failed to register model",
                    status_code=response.status_code,
                    response_text=response.text,
                )
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error registering model: {e!s}")
            raise MosaicConnectionError(str(e)) from e
