"""Tests for SBOM command builder."""

from mais.application.builders.sbom_command_builder import SBOMBuilder


class TestSBOMBuilder:
    """Test cases for SBOMBuilder."""

    def test_create_default_basic(self):
        """Test create_default with no arguments."""
        args = SBOMBuilder.create_default()

        # Check required arguments are present
        assert "generate" in args
        assert "-vvv" in args
        assert "--output" in args
        assert "cyclonedx-json" in args
        assert "--generator" in args
        assert "syft" in args
        assert "--detect-ai" in args  # AI detection should always be enabled
        assert "--install-dependencies" in args
        assert "-f" in args
        assert "sbom" in args
        assert "requirements.txt" in args
        assert "notebook_code.py" in args

        # Check publish is not included by default
        assert "--publish" not in args

    def test_create_default_with_publish(self):
        """Test create_default with publish enabled."""
        args = SBOMBuilder.create_default(publish=True, api_token="test-token")

        # Check publish arguments are included
        assert "--publish" in args
        assert "-k" in args
        assert "test-token" in args

    def test_create_default_with_custom_sources(self):
        """Test create_default with custom source files."""
        custom_sources = ["custom1.txt", "custom2.py"]
        args = SBOMBuilder.create_default(sources=custom_sources)

        # Check custom sources are used
        assert "custom1.txt" in args
        assert "custom2.py" in args
        assert "requirements.txt" not in args
        assert "notebook_code.py" not in args

    def test_ai_detection_always_enabled(self):
        """Test that AI detection is always enabled regardless of parameters."""
        # Test multiple scenarios
        scenarios = [
            {},
            {"publish": True},
            {"api_token": "token"},
            {"sources": ["test.py"]},
        ]

        for kwargs in scenarios:
            args = SBOMBuilder.create_default(**kwargs)
            assert "--detect-ai" in args, (
                f"AI detection not enabled for scenario: {kwargs}"
            )

    def test_builder_methods(self):
        """Test individual builder methods."""
        builder = SBOMBuilder()

        # Test method chaining
        result = (
            builder.with_verbosity("vv")
            .with_output_format("spdx-json")
            .with_generator("trivy")
            .with_ai_detection()
            .with_output_file("test")
            .with_sources(["file1.py", "file2.py"])
            .build()
        )

        assert "generate" in result
        assert "-vv" in result
        assert "--output" in result
        assert "spdx-json" in result
        assert "--generator" in result
        assert "trivy" in result
        assert "--detect-ai" in result
        assert "-f" in result
        assert "test" in result
        assert "file1.py" in result
        assert "file2.py" in result

    def test_builder_reset(self):
        """Test that builder resets after build."""
        builder = SBOMBuilder()

        # First build
        first = builder.with_ai_detection().build()
        assert "--detect-ai" in first

        # Second build should not have AI detection unless added again
        second = builder.with_output_file("test").build()
        assert "--detect-ai" not in second
        assert "-f" in second
        assert "test" in second
