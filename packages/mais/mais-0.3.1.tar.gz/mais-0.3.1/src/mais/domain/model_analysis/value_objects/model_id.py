"""Model ID value object."""


class ModelID:
    """Immutable value object representing a model identifier."""

    def __init__(self, value: str):
        """Initialize ModelID.

        Args:
            value: The model identifier string

        Raises:
            ValueError: If value is empty or invalid
        """
        if not value or not isinstance(value, str):
            raise ValueError("Model ID must be a non-empty string")

        self._value = value.strip()
        self._organization: str | None
        self._name: str

        # Parse organization and model name if present
        parts = self._value.split("/")
        if len(parts) == 2:
            self._organization = parts[0]
            self._name = parts[1]
        else:
            self._organization = None
            self._name = self._value

    @property
    def value(self) -> str:
        """Get the full model ID value."""
        return self._value

    @property
    def name(self) -> str:
        """Get the model name without organization."""
        return self._name

    @property
    def organization(self) -> str | None:
        """Get the organization name if present."""
        return self._organization

    def __str__(self) -> str:
        """String representation."""
        return self._value

    def __repr__(self) -> str:
        """Developer representation."""
        return f"ModelID('{self._value}')"

    def __eq__(self, other) -> bool:
        """Check equality."""
        if not isinstance(other, ModelID):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """Make hashable for use in sets/dicts."""
        return hash(self._value)
