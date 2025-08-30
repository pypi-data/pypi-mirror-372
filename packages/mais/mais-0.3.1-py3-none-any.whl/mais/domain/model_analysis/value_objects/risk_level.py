"""Risk level value object."""

from enum import Enum


class RiskLevel(Enum):
    """Enumeration of model risk levels.

    Each level has a string value and can provide a numeric score.
    """

    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    UNKNOWN = "Unknown"
    INFO = "Info"  # Added to match the constants.py definition

    @classmethod
    def from_string(cls, value: str) -> "RiskLevel":
        """Create RiskLevel from string.

        Args:
            value: Risk level string

        Returns:
            RiskLevel enum value

        Raises:
            ValueError: If value is not a valid risk level
        """
        value = value.capitalize()
        for level in cls:
            if level.value == value:
                return level
        raise ValueError(f"Invalid risk level: {value}")

    @property
    def score(self) -> int:
        """Get numeric score for this risk level."""
        scores = {
            RiskLevel.CRITICAL: 90,
            RiskLevel.HIGH: 70,
            RiskLevel.MEDIUM: 50,
            RiskLevel.LOW: 30,
            RiskLevel.INFO: 10,
            RiskLevel.UNKNOWN: 0
        }
        return scores.get(self, 0)

    @property
    def is_high_risk(self) -> bool:
        """Check if this is a high risk level."""
        # Matching the original HIGH_RISK_LEVELS from constants
        return self in [RiskLevel.CRITICAL, RiskLevel.HIGH]

    @classmethod
    def high_risk_levels(cls) -> list["RiskLevel"]:
        """Get list of high risk levels."""
        return [cls.CRITICAL, cls.HIGH]

    def __str__(self) -> str:
        """String representation."""
        return self.value
