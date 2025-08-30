"""Builder for manifest-cli SBOM generation commands."""


class SBOMBuilder:
    """Builds command arguments for manifest-cli SBOM generation."""

    def __init__(self):
        """Initialize the SBOM builder."""
        self._args = []
        self._reset()

    def with_verbosity(self, level: str = "vvv") -> "SBOMBuilder":
        """Add verbosity flags.

        Args:
            level: Verbosity level (v, vv, vvv)

        Returns:
            Self for chaining
        """
        self._args.append(f"-{level}")
        return self

    def with_output_format(self, format: str = "cyclonedx-json") -> "SBOMBuilder":
        """Set output format.

        Args:
            format: Output format (cyclonedx-json, spdx-json, etc.)

        Returns:
            Self for chaining
        """
        self._args.extend(["--output", format])
        return self

    def with_generator(self, generator: str = "syft") -> "SBOMBuilder":
        """Set SBOM generator.

        Args:
            generator: Generator name (syft, trivy, etc.)

        Returns:
            Self for chaining
        """
        self._args.extend(["--generator", generator])
        return self

    def with_ai_detection(self) -> "SBOMBuilder":
        """Enable AI model detection.

        Returns:
            Self for chaining
        """
        self._args.append("--detect-ai")
        return self

    def with_output_file(self, filename: str = "sbom") -> "SBOMBuilder":
        """Set output filename.

        Args:
            filename: Output filename (without extension)

        Returns:
            Self for chaining
        """
        self._args.extend(["-f", filename])
        return self

    def with_sources(self, sources: list[str]) -> "SBOMBuilder":
        """Add source files/directories.

        Args:
            sources: List of source paths

        Returns:
            Self for chaining
        """
        self._args.extend(sources)
        return self

    def with_path(self, path: str) -> "SBOMBuilder":
        """Add additional path.

        Args:
            path: Directory path

        Returns:
            Self for chaining
        """
        if path and path != "./":
            self._args.append(path)
        return self

    def with_publish(
        self, api_token: str | None = None, api_uri: str | None = None
    ) -> "SBOMBuilder":
        """Enable publishing to MOSAIC.

        Args:
            api_token: API token for authentication

        Returns:
            Self for chaining
        """
        self._args.append("--publish")
        if api_token:
            self._args.extend(["-k", api_token])
        if api_uri:
            self._args.extend(["--api-uri", f"{api_uri}/v1"])
        return self

    def with_install_depenedncies(self) -> "SBOMBuilder":
        """Add --install-dependencies flag with path.
        Returns:
            Self for chaining
        """
        self._args.append("--install-dependencies")
        return self

    def build(self) -> list[str]:
        """Build the final command arguments.

        Returns:
            List of command arguments
        """
        result = self._args.copy()
        self._reset()
        return result

    @classmethod
    def create_default(
        cls,
        sources: list[str] | None = None,
        publish: bool = False,
        api_token: str | None = None,
        api_uri: str | None = None,
    ) -> list[str]:
        """Create default SBOM generation command.

        Args:
            sources: Source files (defaults to requirements.txt and notebook_code.py)
            publish: Whether to publish
            api_token: API token for publishing

        Returns:
            List of command arguments
        """
        builder = cls()

        # Default sources - use relative paths since we'll run in the target directory
        if sources is None:
            sources = ["requirements.txt", "notebook_code.py"]

        # Build command
        builder.with_verbosity("vvv").with_output_format(
            "cyclonedx-json"
        ).with_generator("syft").with_ai_detection()  # Always enable AI detection

        builder.with_install_depenedncies()

        builder.with_output_file("sbom").with_sources(sources)

        if publish:
            builder.with_publish(api_token, api_uri)

        return builder.build()

    def _reset(self) -> None:
        """Reset the builder to initial state."""
        self._args = ["generate"]
