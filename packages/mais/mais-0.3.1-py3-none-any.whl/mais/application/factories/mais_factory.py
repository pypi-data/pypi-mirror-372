"""Factory for creating MAIS instances with different configurations."""

import os

from mais.application.builders import SBOMBuilder
from mais.application.mais_facade import MAIS
from mais.application.services.python_ast_analyzer import ASTAnalyzer
from mais.application.services.risk_assessment_service import RiskAssessmentService
from mais.config import get_config
from mais.domain.model_analysis.repositories import ModelRepository
from mais.infrastructure.api.mosaic_model_repository import MosaicModelRepository


class MAISFactory:
    """Factory for creating configured MAIS instances."""

    @staticmethod
    def create_default(
        verbosity: str = "WARNING",
        api_token: str | None = None
    ) -> MAIS:
        """Create a MAIS instance with default configuration.

        Args:
            verbosity: Logging level
            api_token: API authentication token

        Returns:
            Configured MAIS instance
        """
        return MAIS(
            verbosity=verbosity,
            api_token=api_token
        )

    @staticmethod
    def create_with_custom_risk_analyzer(
        risk_assessment_service: RiskAssessmentService,
        verbosity: str = "WARNING",
        api_token: str | None = None
    ) -> MAIS:
        """Create a MAIS instance with a custom risk analyzer.

        Args:
            risk_assessment_service: Custom RiskAssessmentService instance
            verbosity: Logging level
            api_token: API authentication token

        Returns:
            Configured MAIS instance
        """
        config = get_config()
        api_url = os.getenv("MOSAIC_API_URL", config.mosaic_api_url)
        api_token = api_token or os.getenv("MANIFEST_API_TOKEN")

        # Create matching model repository
        model_repository = MosaicModelRepository(
            api_url=api_url,
            api_token=api_token,
            enabled=True
        )

        return MAIS(
            verbosity=verbosity,
            api_token=api_token,
            risk_assessment_service=risk_assessment_service,
            model_repository=model_repository
        )

    @staticmethod
    def create_offline(verbosity: str = "WARNING") -> MAIS:
        """Create a MAIS instance for offline use (no API connections).

        Args:
            verbosity: Logging level

        Returns:
            Configured MAIS instance for offline use
        """
        # Create disabled components
        model_repository = MosaicModelRepository(
            api_url="",
            api_token="",
            enabled=False
        )

        risk_assessment_service = RiskAssessmentService()

        return MAIS(
            verbosity=verbosity,
            mosaic_enabled=False,
            model_repository=model_repository,
            risk_assessment_service=risk_assessment_service
        )

    @staticmethod
    def create_for_testing(
        model_repository: ModelRepository | None = None,
        risk_assessment_service: RiskAssessmentService | None = None,
        ast_analyzer: ASTAnalyzer | None = None,
        sbom_builder: SBOMBuilder | None = None
    ) -> MAIS:
        """Create a MAIS instance for testing with mock components.

        Args:
            model_repository: Mock model repository
            risk_assessment_service: Mock risk assessment service
            ast_analyzer: Mock AST analyzer
            sbom_builder: Mock SBOM builder

        Returns:
            Configured MAIS instance for testing
        """
        return MAIS(
            verbosity="DEBUG",
            mosaic_enabled=False,
            model_repository=model_repository,
            risk_assessment_service=risk_assessment_service,
            ast_analyzer=ast_analyzer,
            sbom_builder=sbom_builder
        )
