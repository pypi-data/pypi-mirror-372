"""SBOM format value object."""

from enum import Enum


class SBOMFormat(Enum):
    """Supported SBOM formats."""

    CYCLONEDX_JSON = "cyclonedx-json"
    CYCLONEDX_XML = "cyclonedx-xml"
    SPDX_JSON = "spdx-json"
    SPDX_TAG_VALUE = "spdx-tag-value"

    def __str__(self) -> str:
        """String representation."""
        return self.value
