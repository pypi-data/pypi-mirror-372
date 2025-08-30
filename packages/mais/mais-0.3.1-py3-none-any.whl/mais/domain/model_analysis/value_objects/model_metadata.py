"""Model metadata value object."""

from pydantic import BaseModel, Field


class ModelMetadata(BaseModel):
    """Immutable value object representing model metadata.

    Contains essential information about a detected/loaded model.
    """

    name: str | None = Field(None, description="Name of the model")
    supplier: str | None = Field(None, description="Model supplier/provider")
    version: str | None = Field(None, description="Model version")
    supplier_country: str | None = Field(
        None, description="Country of the supplier"
    )

    class Config:
        """Pydantic configuration."""

        frozen = True  # Makes it immutable

    @classmethod
    def from_dict(cls, data: dict) -> "ModelMetadata":
        """Create ModelMetadata from dictionary."""
        return cls(
            name=data.get("name"),
            supplier=data.get("supplier"),
            version=data.get("version"),
            supplier_country=data.get("supplier_country"),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return self.dict(exclude_none=True)

    def __str__(self) -> str:
        """String representation."""
        parts = []
        if self.supplier:
            parts.append(self.supplier)
        if self.name:
            parts.append(self.name)
        if self.version:
            parts.append(f"v{self.version}")
        return "/".join(parts) if parts else "Unknown Model"
