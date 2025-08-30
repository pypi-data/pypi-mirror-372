"""Application service for model analysis."""

from mais.application.services.python_ast_analyzer import ASTAnalyzer
from mais.application.services.risk_assessment_service import (
    RiskAssessmentService,
)
from mais.config import get_config
from mais.domain.exceptions import ModelNotApprovedError
from mais.domain.model_analysis.entities import ModelRiskAssessment
from mais.domain.model_analysis.repositories import ModelRepository
from mais.domain.model_analysis.value_objects import ModelID
from mais.domain.model_analysis.value_objects.model_metadata import (
    ModelMetadata,
)
from mais.utils.logger import logger


class ModelAnalysisService:
    """Application service orchestrating model analysis."""

    def __init__(
        self,
        model_repository: ModelRepository,
        risk_assessment_service: RiskAssessmentService,
        ast_analyzer: ASTAnalyzer,
    ):
        """Initialize the model analysis service.

        Args:
            model_repository: Repository for model data
            risk_assessment_service: Service for risk assessment
            ast_analyzer: AST analyzer for code parsing
        """
        self.model_repository = model_repository
        self.risk_assessment_service = risk_assessment_service
        self.ast_analyzer = ast_analyzer
        self.logger = logger

    def analyze_code(
        self, code: str
    ) -> tuple[list[ModelRiskAssessment], list[ModelNotApprovedError], list]:
        """Analyze code for model loads and assess risks.

        Args:
            code: Python code to analyze

        Returns:
            Tuple of (risk assessments, unapproved model errors)
        """
        try:
            class_aliases, variable_models, call_nodes = self._parse_code(code)
            datasets = self.ast_analyzer.extract_dataset(code)
            risk_assessments = []
            unapproved_errors = []

            for call_node in call_nodes:
                assessments, errors = self._process_function_call(
                    call_node, class_aliases, variable_models
                )
                risk_assessments.extend(assessments)
                unapproved_errors.extend(errors)

            return risk_assessments, unapproved_errors, datasets

        except SyntaxError:
            raise
        except Exception as e:
            self.logger.error(f"Error analyzing code: {e!s}")
            raise

    def _parse_code(
        self, code: str
    ) -> tuple[dict[str, str], dict[str, str], list]:
        """Parse code and extract model loading information.

        Args:
            code: Python code to parse

        Returns:
            Tuple of (class_aliases, variable_models, call_nodes)
        """
        return self.ast_analyzer.analyze_code(code)

    def _process_function_call(
        self,
        call_node,
        class_aliases: dict[str, str],
        variable_models: dict[str, str],
    ) -> tuple[list[ModelRiskAssessment], list[ModelNotApprovedError]]:
        """Process a single function call for model loading.

        Args:
            call_node: AST call node to process
            class_aliases: Dictionary of class aliases
            variable_models: Dictionary of variable model assignments

        Returns:
            Tuple of (risk assessments, unapproved errors) for this call
        """
        func_path, is_alias_match = self.ast_analyzer.resolve_function_path(
            call_node.func, class_aliases
        )

        if not self._is_watched_function(func_path, is_alias_match):
            return [], []

        models = self._extract_models_from_call(call_node, variable_models)

        risk_assessments = []
        unapproved_errors = []

        for model_name, _display_name, _ in models:
            model_id = ModelID(model_name)

            error = self._check_if_model_is_approved(model_id, func_path)
            if error:
                unapproved_errors.append(error)
                continue

            assessment = self._get_model_data_and_assess_risk(model_id)
            if assessment:
                risk_assessments.append(assessment)

        return risk_assessments, unapproved_errors

    def _is_watched_function(
        self, func_path: str | None, is_alias_match: bool
    ) -> bool:
        """Check if a function should be analyzed for model loading.

        Args:
            func_path: Function path to check
            is_alias_match: Whether this is an alias match

        Returns:
            True if function should be analyzed
        """
        return (
            func_path and self.ast_analyzer.function_matches_watched(func_path)
        ) or is_alias_match

    def _extract_models_from_call(
        self, call_node, variable_models: dict[str, str]
    ) -> list:
        """Extract model information from a function call.

        Args:
            call_node: AST call node
            variable_models: Dictionary of variable model assignments

        Returns:
            List of model information tuples
        """
        return self.ast_analyzer.extract_model_from_call(
            call_node, variable_models
        )

    def _check_if_model_is_approved(
        self, model_id: ModelID, func_path: str | None
    ) -> ModelNotApprovedError | None:
        """Check if a model is approved and return error if not.

        Args:
            model_id: Model identifier to check
            func_path: Function path attempting to load the model

        Returns:
            ModelNotApprovedError if not approved, None otherwise
        """
        if not self.model_repository.is_approved(model_id):
            return ModelNotApprovedError(
                model_id=str(model_id),
                func_path=func_path,
                error="Model not in approved inventory",
            )
        return None

    def _get_model_data_and_assess_risk(
        self, model_id: ModelID
    ) -> ModelRiskAssessment | None:
        """Get model data and assess its risk.

        Args:
            model_id: Model identifier to assess

        Returns:
            Risk assessment if model data found, None otherwise
        """
        model_data = self.model_repository.find_by_id(model_id)
        if model_data:
            return self.risk_assessment_service.assess_risk(
                model_id, model_data
            )
        return None

    def trigger_quickscan_analysis(self, model_id: str) -> dict[str, str]:
        """Trigger quickscan analysis for a model.

        Args:
            model_id: Model identifier to analyze
        Returns:
            Quickscan results as a dictionary
        """
        quickscan_results = self.model_repository.trigger_quickscan_analysis(
            model_id
        )
        return quickscan_results

    def get_model_data_from_model_analysis(self, model_id: str) -> dict | None:
        """Get model data from model analysis.

        Args:
            model_id: Model identifier to retrieve data for

        Returns:
            Model data if available, None otherwise
        """
        return self.model_repository.get_model_data_from_model_analysis(
            model_id
        )

    def register_model(
        self,
        model_name: str,
        model_version: str,
        supplier: str,
        supplier_country: str,
        software_dependencies: list,
        datasets: list,
        base_model_data: ModelMetadata | None = None,
    ) -> ModelID:
        """Register a new model in the repository.

        Args:
            model_id: Model identifier to register
            model_data: Data associated with the model
        """
        if base_model_data is None:
            raise ValueError("base_model_data must be provided")
        model_id = self.model_repository.register_model(
            model_name,
            model_version,
            supplier,
            supplier_country,
            software_dependencies,
            datasets,
            base_model_data,
        )
        self.logger.debug(f"Registered new model {model_id}")
        return model_id

    def get_finetuning_model_from_code(
        self, code: str, loaded_models: list[str]
    ) -> str | None:
        """Check if fine-tuning was initiated and return the model used.

        Args:
            code: Python code to analyze

        Returns:
            Model name/id if fine-tuning was detected with a model parameter, None otherwise
        """
        try:
            config = (
                get_config()
            )  # Get config to access finetuning functions/classes
            class_aliases, variable_models, call_nodes = self._parse_code(code)

            for call_node in call_nodes:
                func_path, is_alias_match = (
                    self.ast_analyzer.resolve_function_path(
                        call_node.func, class_aliases
                    )
                )

                # Check if this is a fine-tuning function/class
                is_finetuning_func = (
                    func_path in config.finetuning_functions
                    or (
                        func_path
                        and any(
                            ft_func in func_path
                            for ft_func in config.finetuning_functions
                        )
                    )
                    or (
                        func_path
                        and func_path.split(".")[-1]
                        in config.finetuning_classes
                    )
                    or (
                        is_alias_match
                        and any(
                            alias in config.finetuning_classes
                            for alias in class_aliases.values()
                        )
                    )
                )

                if is_finetuning_func:
                    models = self._extract_models_from_call(
                        call_node, variable_models
                    )
                    if models:
                        model_name, _, _ = models[0]
                        return model_name

            # fall back to most recently loaded model
            if loaded_models and len(loaded_models) > 0:
                return loaded_models[-1]

            return None

        except Exception as e:
            self.logger.error(f"Error checking for fine-tuning: {e}")
            return None
