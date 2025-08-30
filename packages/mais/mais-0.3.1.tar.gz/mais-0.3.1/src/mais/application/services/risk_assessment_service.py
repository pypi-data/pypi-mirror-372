"""Domain service for risk assessment."""

from typing import Any

from mais.domain.model_analysis.entities import ModelRiskAssessment
from mais.domain.model_analysis.value_objects import ModelID, RiskLevel


class RiskAssessmentService:
    """Service for assessing model risks."""

    def assess_risk(
        self, model_id: ModelID, model_data: dict[str, Any] | None = None
    ) -> ModelRiskAssessment:
        """Assess risk for a model.

        Args:
            model_id: The model identifier
            model_data: Optional model data from repository

        Returns:
            Risk assessment for the model
        """
        if not model_data:
            return ModelRiskAssessment(
                model_id=model_id,
                risk_level=RiskLevel.UNKNOWN,
                findings=["Model data not available for risk assessment"],
            )

        # Extract risk information
        risk_score = model_data.get("riskScore", "Unknown")
        try:
            risk_level = RiskLevel.from_string(risk_score)
        except ValueError:
            risk_level = RiskLevel.UNKNOWN

        # Create assessment
        assessment = ModelRiskAssessment(
            model_id=model_id,
            risk_level=risk_level,
            model_name=model_data.get("name", str(model_id)),
            in_inventory=True,
        )

        return assessment

    def enhance_with_findings(
        self, assessment: ModelRiskAssessment, findings: list[str]
    ) -> None:
        """Add findings to an existing assessment.

        Args:
            assessment: The risk assessment to enhance
            findings: List of findings to add
        """
        for finding in findings:
            if finding:
                assessment.add_finding(finding)
