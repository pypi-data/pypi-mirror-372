"""Custom exceptions for MAIS."""


class MAISError(Exception):
    """Base exception for all MAIS errors."""

    pass


class ModelNotFoundError(MAISError):
    """Raised when a model is not found in the inventory."""

    def __init__(self, model_id: str, message: str | None = None):
        self.model_id = model_id
        self.message = message or f"Model '{model_id}' not found in inventory"
        super().__init__(self.message)


class ModelNotApprovedError(MAISError):
    """Raised when a model is not approved for use."""

    def __init__(
        self, model_id: str, func_path: str | None = None, error: str | None = None
    ):
        self.model_id = model_id
        self.func_path = func_path
        self.error = error
        message = f"Model '{model_id}' is not approved for use"
        if func_path:
            message = f"Function `{func_path}` is trying to load unapproved model `{model_id}`"
        if error:
            message += f" ({error})"
        super().__init__(message)


class MosaicAPIError(MAISError):
    """Raised when there's an error communicating with the MOSAIC API."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_text: str | None = None,
    ):
        self.status_code = status_code
        self.response_text = response_text
        if status_code:
            message = f"MOSAIC API error: {status_code} - {message}"
        super().__init__(message)


class MosaicConnectionError(MosaicAPIError):
    """Raised when connection to MOSAIC API fails."""

    def __init__(self, message: str):
        super().__init__(f"Failed to connect to MOSAIC API: {message}")


class MosaicAuthenticationError(MosaicAPIError):
    """Raised when authentication with MOSAIC API fails."""

    def __init__(self, message: str | None = None):
        super().__init__(
            message or "Authentication failed: Invalid or missing API token",
            status_code=401,
        )


class RiskAssessmentError(MAISError):
    """Raised when there's an error assessing model risk."""

    def __init__(self, model_id: str, message: str):
        self.model_id = model_id
        super().__init__(f"Error assessing risk for model '{model_id}': {message}")


class SBOMGenerationError(MAISError):
    """Raised when SBOM generation fails."""

    def __init__(self, message: str, stderr: str | None = None):
        self.stderr = stderr
        if stderr:
            message = f"{message}: {stderr}"
        super().__init__(message)


class ConfigurationError(MAISError):
    """Raised when there's a configuration error."""

    pass


class DependencyError(MAISError):
    """Raised when a required dependency is missing."""

    def __init__(self, dependency: str, message: str | None = None):
        self.dependency = dependency
        self.message = message or f"Required dependency '{dependency}' is not available"
        super().__init__(self.message)
