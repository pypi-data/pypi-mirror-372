"""Model risk assessment entity."""


from mais.domain.model_analysis.value_objects import ModelID, RiskLevel


class ModelRiskAssessment:
    """Entity representing a risk assessment for a model."""

    def __init__(
        self,
        model_id: ModelID,
        risk_level: RiskLevel,
        findings: list[str] | None = None,
        model_name: str | None = None,
        in_inventory: bool = False,
    ):
        """Initialize risk assessment.

        Args:
            model_id: The model identifier
            risk_level: The assessed risk level
            findings: List of risk findings
            model_name: Optional display name for the model
            in_inventory: Whether the model is in the inventory
        """
        self.model_id = model_id
        self.risk_level = risk_level
        self.findings = findings or []
        self.model_name = model_name or str(model_id)
        self.in_inventory = in_inventory

    @property
    def is_high_risk(self) -> bool:
        """Check if this is a high risk assessment."""
        return self.risk_level.is_high_risk

    def add_finding(self, finding: str) -> None:
        """Add a risk finding.

        Args:
            finding: Risk finding description
        """
        if finding and finding not in self.findings:
            self.findings.append(finding)

    def format_findings(self) -> str:
        """Format findings for display.

        Returns:
            Formatted findings string
        """
        if not self.findings:
            return "No specific findings reported."
        return "\n\n".join(f"\n- {finding}" for finding in self.findings)

    def __repr__(self) -> str:
        """Developer representation."""
        return (
            f"ModelRiskAssessment(model_id={self.model_id}, "
            f"risk_level={self.risk_level}, findings={len(self.findings)})"
        )
