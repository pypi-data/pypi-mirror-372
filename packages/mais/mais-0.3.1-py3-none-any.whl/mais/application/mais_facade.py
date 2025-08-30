"""MAIS Facade - Main entry point for the ML Model Audit & Inspection System."""

from mais.application.builders import SBOMBuilder
from mais.application.services import ModelAnalysisService
from mais.application.services.model_session_service import ModelSessionService
from mais.application.services.python_ast_analyzer import ASTAnalyzer
from mais.application.services.risk_assessment_service import (
    RiskAssessmentService,
)
from mais.config import get_config
from mais.domain.model_analysis.repositories import ModelRepository
from mais.infrastructure.api.mosaic_model_repository import (
    MosaicModelRepository,
)
from mais.presentation.jupyter.mais_plugin import JupyterPlugin
from mais.utils.logger import logger


class MAIS:
    """Main MAIS class - facade for the entire system.

    This facade provides a unified interface to the MAIS system, hiding the
    complexity of the underlying DDD architecture from users who just want
    to use MAIS for model security scanning.
    """

    def __init__(
        self,
        verbosity: str | None = None,
        mosaic_api_url: str | None = None,
        mosaic_enabled: bool | None = None,
        api_token: str | None = None,
        # Optional injected dependencies
        model_repository: ModelRepository | None = None,
        risk_assessment_service: RiskAssessmentService | None = None,
        ast_analyzer: ASTAnalyzer | None = None,
        sbom_builder: SBOMBuilder | None = None,
    ):
        """Initialize MAIS.

        This is a facade that sets up the entire system using DDD architecture.

        Args:
            verbosity: Logging level
            mosaic_api_url: MOSAIC API URL
            mosaic_enabled: Whether to enable MOSAIC integration
            api_token: API authentication token
            model_repository: Optional custom model repository
            risk_assessment_service: Optional custom risk assessment service
            ast_analyzer: Optional custom AST analyzer
            sbom_builder: Optional custom SBOM builder
        """
        # Get configuration
        config = get_config()

        # Use provided values or fall back to config
        verbosity = verbosity or config.default_verbosity
        api_url = mosaic_api_url or config.mosaic_api_url
        api_token = api_token or config.manifest_api_token
        mosaic_enabled = (
            mosaic_enabled
            if mosaic_enabled is not None
            else config.mosaic_enabled
        )

        # Create or use injected infrastructure components
        self._model_repository: ModelRepository = (
            model_repository
            or MosaicModelRepository(
                api_url=api_url, api_token=api_token, enabled=mosaic_enabled
            )
        )

        # Check connection if MOSAIC is enabled, otherwise disable it
        if mosaic_enabled and hasattr(
            self._model_repository, "check_connection"
        ):
            is_connected = self._model_repository.check_connection()
            if not is_connected:
                logger.warning(
                    "MOSAIC API connection failed. Disabling MOSAIC integration."
                )
                if hasattr(self._model_repository, "enabled"):
                    self._model_repository.enabled = False
                self.mosaic_enabled = False

        # Create or use injected domain services
        self._risk_assessment_service = (
            risk_assessment_service or RiskAssessmentService()
        )

        # Create or use injected infrastructure services
        self._ast_analyzer = ast_analyzer or ASTAnalyzer()
        self._sbom_builder = sbom_builder or SBOMBuilder()

        # Create application service
        self._model_analysis_service = ModelAnalysisService(
            model_repository=self._model_repository,
            risk_assessment_service=self._risk_assessment_service,
            ast_analyzer=self._ast_analyzer,
        )

        # Create session service for detected models
        self._model_session_service = ModelSessionService()

        # Create presentation layer
        self._plugin = JupyterPlugin(
            model_analysis_service=self._model_analysis_service,
            model_session_service=self._model_session_service,
            sbom_builder=self._sbom_builder,
            api_token=api_token,
            api_uri=api_url,
            verbosity=verbosity,
        )

        # Store configuration for backward compatibility
        self.verbosity = verbosity
        self.mosaic_api_url = api_url
        self.mosaic_enabled = mosaic_enabled
        self.api_token = api_token
        self.logger = self._plugin.logger

    # Delegate to plugin for backward compatibility
    def set_verbosity(self, level: str = "WARNING") -> None:
        """Set logging verbosity level."""
        self._plugin.set_verbosity(level)
        self.verbosity = level

    def set_url(self, url: str) -> None:
        """Set MOSAIC API URL."""
        # Update repository if it's a MOSAIC repository
        if hasattr(self._model_repository, "api_url"):
            self._model_repository.api_url = url
        self.mosaic_api_url = url

    def create_sbom(self, path: str = "./", publish: bool = False) -> None:
        """Create Software Bill of Materials."""
        self._plugin.create_sbom(path, publish)

    def read_sbom(self, path: str) -> str:
        """Read SBOM file from the specified path."""
        return self._plugin.read_sbom(path)

    def display_warning(self, title: str, message: str) -> None:
        """Display a warning to the user."""
        self._plugin.display_warning(title, message)

    def register_hooks(self) -> None:
        """Register IPython hooks."""
        self._plugin.register_hooks()

    def analyze_code_for_model_loads(self, code: str) -> bool:
        """Analyze code for risky model loads (backward compatibility)."""
        risk_assessments, unapproved_errors, _ = (
            self._model_analysis_service.analyze_code(code)
        )
        return bool(risk_assessments or unapproved_errors)

    def set_base_model(self, base_model_name: str) -> None:
        """Set the base model for analysis."""
        self._plugin.set_base_model(base_model_name)

    def register_model(
        self,
        model_name: str,
        model_version: str,
        supplier: str,
        supplier_country: str,
    ) -> None:
        """Register a model in the repository."""
        self._plugin.register_model(
            model_name=model_name,
            model_version=model_version,
            supplier=supplier,
            supplier_country=supplier_country,
        )
