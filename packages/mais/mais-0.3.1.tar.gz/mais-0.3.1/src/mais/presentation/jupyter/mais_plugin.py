"""MAIS Jupyter plugin presentation layer."""

import logging
import os
from pathlib import Path
import time

from IPython import get_ipython
from IPython.display import Markdown, display

from mais.application.builders import SBOMBuilder
from mais.application.services import ModelAnalysisService
from mais.application.services.model_session_service import ModelSessionService
from mais.domain.exceptions import (
    SBOMGenerationError,
)
from mais.domain.model_analysis.entities.model_risk_assessment import (
    ModelRiskAssessment,
)
from mais.domain.model_analysis.value_objects import ModelID, ModelMetadata
from mais.utils.logger import logger
from mais.utils.notebook import get_current_notebook_data, save_all_code_to_temp
from mais.utils.sbom_generation import pip_freeze, run_manifest_cli


class JupyterPlugin:
    """Jupyter notebook plugin for MAIS."""

    def __init__(
        self,
        model_analysis_service: ModelAnalysisService,
        model_session_service: ModelSessionService,
        sbom_builder: SBOMBuilder | None = None,
        api_token: str | None = None,
        api_uri: str | None = None,
        verbosity: str = "WARNING",
    ):
        """Initialize Jupyter plugin.

        Args:
            model_analysis_service: Service for model analysis
            sbom_builder: Optional SBOM command builder
            api_token: API token for publishing
            verbosity: Logging level
        """
        self.model_analysis_service = model_analysis_service
        self.model_session_service = model_session_service
        self.sbom_builder = sbom_builder or SBOMBuilder()
        self.api_token = api_token or os.getenv("MANIFEST_API_TOKEN")
        self.api_uri = api_uri
        self.logger = logger

        self.set_verbosity(verbosity)
        self.register_hooks()
        self.logger.debug("Jupyter plugin initialized")
        self._initial_pip_freeze = pip_freeze()
        self.logger.debug(f"Initial pip freeze: {self._initial_pip_freeze}")
        self._datasets: list[str] = []
        self._base_model: ModelMetadata | None = None

    def set_base_model(self, base_model_key=None) -> None:
        """Set the base model for the plugin.

        Args:
            base_model_key: Key to identify the base model

        Raises:
            ValueError: If the base model key is invalid
        """

        loaded_models = self.model_session_service.list_detected_models()
        if not loaded_models:
            self.logger.error("No models loaded in the repository")
            raise ValueError("No models loaded in the repository")
        self.logger.info(
            f"Finding {base_model_key} loaded models: {loaded_models}"
        )
        if base_model_key and base_model_key in loaded_models:
            self._base_model = loaded_models[base_model_key]
            self.logger.warning(f"Base model set: {self._base_model}")
        else:
            self.logger.warning(
                f"Base model '{base_model_key}' not found in loaded models. Using latest loaded model"
            )
            self._base_model = list(loaded_models.values())[-1]

    def set_verbosity(self, level: str = "WARNING") -> None:
        """Set logging verbosity level."""
        numeric_level = getattr(logging, level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f"Invalid log level: {level}")
        self.logger.setLevel(numeric_level)
        self.logger.debug(f"Logging level set to {level}")

    def display_warning(self, title: str, message: str) -> None:
        """Display a warning to the user, styled like the findings image."""
        try:
            import ipywidgets as widgets

            HAS_WIDGETS = True
        except ImportError:
            HAS_WIDGETS = False

        if get_ipython() is not None:
            if HAS_WIDGETS:
                self.logger.debug(f"Displaying warning: {title} - {message}")

                # Title formatting
                title_html = f'<div style="font-size:13px; font-weight:bold; margin-bottom: 15px">{title}</div>'
                html_message = self._markdown_links_to_html(message)
                # Split message into warnings (lines)
                warnings = [
                    line.strip()
                    for line in html_message.strip().split("\n")
                    if line.strip()
                ]

                # Build HTML for warnings
                warnings_html = ""
                for warning in warnings:
                    warnings_html += (
                        '<div style="display:flex;align-items:center;margin-bottom:4px;">'
                        f'<span style="color:#f7f8f8">{warning}</span>'
                        "</div>"
                    )

                html_message = f"""
                    <div style="border:2px solid #23272f; background-color:#181c23; color:#e6e6e6; padding:18px; border-radius:10px; margin:12px 0; font-family: 'Inter', sans-serif;">
                        <div style="font-size:13px; letter-spacing:2px; color:#8a8fa3; margin-bottom:10px; font-weight:600;">MAIS</div>
                        {title_html}
                        {warnings_html}
                    </div>
                    """
                box = widgets.HTML(value=html_message)
                display(box)
            else:
                display(Markdown(f"**{title}**\n\n{message}"))
        else:
            self.logger.warning(f"**{title}**\n\n{message}")

    def display_info(self, title: str, message: str) -> None:
        """Display an informational message to the user, styled like MAIS info."""
        try:
            import ipywidgets as widgets

            HAS_WIDGETS = True
        except ImportError:
            HAS_WIDGETS = False

        if get_ipython() is not None:
            if HAS_WIDGETS:
                self.logger.debug(f"Displaying info: {message}")

                # Title formatting
                title_html = f'<div style="font-size:13px; font-weight:bold; margin-bottom: 15px">{title}</div>'
                # Convert Markdown links to HTML
                html_message = self._markdown_links_to_html(message)
                # Split message into lines
                info_lines = [
                    line.strip()
                    for line in html_message.strip().split("\n")
                    if line.strip()
                ]

                # Build HTML for info lines
                info_html = ""
                for line in info_lines:
                    info_html += (
                        '<div style="display:flex;align-items:center;margin-bottom:4px;">'
                        f'<span style="color:#f7f8f8">{line}</span>'
                        "</div>"
                    )

                html_message = f"""
                    <div style="border:2px solid #2d3a4d; background-color:#1a2230; color:#e6e6e6; padding:18px; border-radius:10px; margin:12px 0; font-family: 'Inter', sans-serif;">
                        <div style="font-size:13px; letter-spacing:2px; color:#8a8fa3; margin-bottom:10px; font-weight:600;">MAIS</div>
                        {title_html}
                        {info_html}
                    </div>
                    """
                box = widgets.HTML(value=html_message)
                display(box)
            else:
                display(Markdown(f"**MAIS**\n\n{message}"))
        else:
            self.logger.info(f"**MAIS**\n\n{message}")

    def register_hooks(self) -> None:
        """Register IPython hooks for code analysis."""
        ip = get_ipython()
        if not ip:
            self.logger.warning(
                "Not running in IPython environment, hooks not registered"
            )
            return

        self.logger.debug("Setting up IPython hooks")

        def mais_pre_run_hook(info):
            """Hook to analyze code before execution."""
            self.logger.debug("Pre-run hook triggered")
            code = info.raw_cell
            self.logger.debug(f"Cell code: {code}")

            # Skip shell and magic commands
            if code.strip().startswith("!") or code.strip().startswith("%"):
                self.logger.debug("Skipping analysis of shell/magic command")
                return

            try:
                # Analyze code
                risk_assessments, unapproved_errors, datasets = (
                    self.model_analysis_service.analyze_code(code)
                )
                self.logger.debug(f"Datasets found: {datasets}")

                # Collect datasets
                self._collect_datasets(datasets)

                # Handle unapproved models
                self._handle_unapproved_models(unapproved_errors)

                # Display risk warnings
                self._display_risk_warnings(risk_assessments)

                # Find fine-tuning models and set as base model, otherwise use latest model loaded
                if self._base_model is None:
                    loaded_models = (
                        self.model_session_service.list_detected_models()
                    )
                    base_model = self.model_analysis_service.get_finetuning_model_from_code(
                        code, list(loaded_models.keys())
                    )
                    if base_model:
                        self.logger.debug(f"Base model detected: {base_model}")
                        self.set_base_model(base_model)

            except SyntaxError as e:
                self.logger.debug(f"Skipping analysis due to syntax error: {e}")

        # Clear existing hooks
        self.logger.debug("Clearing existing IPython hooks")
        if hasattr(ip.events, "callbacks") and ip.events.callbacks.get(
            "pre_run_cell", None
        ):
            existing_pre_cell_hooks = ip.events.callbacks["pre_run_cell"]
            if existing_pre_cell_hooks and len(existing_pre_cell_hooks) > 0:
                for hook in existing_pre_cell_hooks:
                    if (
                        hasattr(hook, "__name__")
                        and hook.__name__ == "mais_pre_run_hook"
                    ):
                        self.logger.debug(
                            f"Unregistering pre_run_cell hook: {hook.__name__}"
                        )
                        ip.events.unregister("pre_run_cell", hook)

        # Register new hook
        ip.events.register("pre_run_cell", mais_pre_run_hook)
        self.logger.debug("IPython hooks successfully registered")

    def create_sbom(self, path: str = "./", publish: bool = False) -> None:
        """Create Software Bill of Materials for the project.

        Args:
            path: Directory to create SBOM in
            publish: Whether to publish to Manifest API

        Raises:
            SBOMGenerationError: If any step of SBOM generation fails
        """
        # Create directory if needed
        if not os.path.exists(path):
            os.makedirs(path)

        self.logger.debug(f"Creating SBOM in path: {path}")

        # Generate requirements and code files
        current_freeze = pip_freeze()
        self.logger.debug(f"Current pip freeze: {current_freeze}")
        diff_packages = list(
            set(current_freeze) - set(self._initial_pip_freeze)
        )
        self.logger.debug(f"Diff packages for SBOM: {diff_packages}")
        save_all_code_to_temp(path=path)

        # Wait for files to be created
        requirements_path = Path(path) / "requirements.txt"
        with open(requirements_path, "a") as f:
            for pkg in diff_packages:
                f.write(pkg + "\n")
        notebook_path = Path(path) / "notebook_code.py"

        max_wait = 5  # seconds
        waited = 0.0
        while (
            not requirements_path.exists() or not notebook_path.exists()
        ) and waited < max_wait:
            self.logger.debug(
                "Waiting for requirements.txt and notebook_code.py to be created..."
            )
            time.sleep(0.5)
            waited += 0.5

        if not requirements_path.exists() or not notebook_path.exists():
            raise SBOMGenerationError(
                "Failed to create required files for SBOM generation"
            )

        self.logger.debug(
            "Both requirements.txt and notebook_code.py files are ready"
        )

        # Set API token for manifest-cli
        if self.api_token:
            os.environ["MANIFEST_API_KEY"] = self.api_token

        # Build manifest-cli arguments
        args = SBOMBuilder.create_default(
            publish=publish,
            api_token=self.api_token if publish else None,
            api_uri=self.api_uri if publish else None,
        )

        # Run manifest-cli with the path as working directory
        self.logger.debug(f"Running manifest-cli with args: {args}")
        if self.api_token:
            result = run_manifest_cli(args, cwd=path, api_key=self.api_token)
        else:
            result = run_manifest_cli(args, cwd=path)

        # Check for errors
        if result.stderr:
            self.logger.error(f"Manifest-cli error: {result.stderr}")

        if result.returncode != 0:
            self.logger.error(
                f"Manifest-cli failed with return code: {result.returncode}"
            )
            raise SBOMGenerationError("Manifest-cli failed", result.stderr)

        self.logger.debug(f"Manifest-cli output: {result.stdout}")
        self.logger.debug(f"Full result: {result}")

        # Verify SBOM was created
        sbom_path = Path(path) / "sbom.json"
        if not sbom_path.exists():
            raise SBOMGenerationError(
                "SBOM file was not created by manifest-cli"
            )

        self.logger.debug(f"SBOM successfully created at {sbom_path}")
        self.display_info(
            "✅ SBOM Created",
            f"SBOM file created successfully at `{sbom_path}`.\n"
            "You can view the content of the SBOM below.",
        )
        self.read_sbom(path)

    def read_sbom(self, path: str) -> str:
        """Read SBOM file from the specified path.

        Args:
            path: Directory containing the sbom.json file

        Returns:
            Content of the SBOM file

        Raises:
            SBOMGenerationError: If the file cannot be read
        """
        sbom_path = Path(path) / "sbom.json"
        try:
            with open(sbom_path) as f:
                import json

                content = f.read()
                self.logger.debug("Successfully read SBOM file")
                sbom_json = json.loads(content)
                readable_sbom = json.dumps(sbom_json, indent=2)
                self.logger.debug("Formatted SBOM content for readability")
                self.display_info("📄 SBOM Content", readable_sbom)
                return content
        except FileNotFoundError as e:
            raise SBOMGenerationError("SBOM file 'sbom.json' not found") from e
        except Exception as e:
            raise SBOMGenerationError(f"Error reading SBOM file: {e!s}") from e

    def register_model(
        self,
        model_name: str,
        model_version: str,
        supplier: str,
        supplier_country: str,
    ) -> None:
        """Register a model with the plugin.

        Args:
            model_name: Name of the model
            model_version: Version of the model
            supplier: Supplier of the model
            supplier_country: Country of the supplier
            base_model: Optional base model name to use for registration

        Raises:
            ValueError: If the model ID is already registered
        """
        current_notebook = get_current_notebook_data()
        current_freeze = pip_freeze()
        self.logger.debug(f"Current pip freeze: {current_freeze}")
        self.logger.debug(f"Current notebook data: {current_notebook}")
        diff_packages = list(
            set(current_freeze) - set(self._initial_pip_freeze)
        )
        self.logger.debug(
            f"Diff packages for model registration: {diff_packages}"
        )
        software_dependencies = [
            {
                "library": dep.split("==")[0],
                "version": dep.split("==")[1] if "==" in dep else "unknown",
                "foundIn": current_notebook.get("name", "unknown"),
            }
            for dep in diff_packages
        ]
        if not software_dependencies:
            self.logger.warning(
                "No software dependencies found for model registration, using empty list"
            )
            software_dependencies = []
        self.logger.debug(
            f"Software dependencies for model registration: {software_dependencies}"
        )
        self.logger.debug(f"Datasets for model registration: {self._datasets}")

        # Set base model if not already set
        self.logger.debug(self._base_model)
        self.logger.debug("Checking if base model is set for registration")
        if not self._base_model:
            self.set_base_model()

        registered_model_id = self.model_analysis_service.register_model(
            model_name,
            model_version,
            supplier,
            supplier_country,
            software_dependencies,
            datasets=self._datasets,
            base_model_data=self._base_model,
        )
        self.logger.debug(f"Registered model ID: {registered_model_id.value}")
        custom_model_inventory_url = self._get_custom_model_inventory_url(
            registered_model_id.value, self.api_uri
        )
        if custom_model_inventory_url:
            self.logger.debug(
                f"Custom model inventory URL: {custom_model_inventory_url}"
            )
            self.display_info(
                f"✅ Custom Model '{model_name}' registered successfully.",
                f"🔍 [View Custom Model in Inventory]({custom_model_inventory_url})\n"
                f"{custom_model_inventory_url}\n",
            )

    def _collect_datasets(self, datasets: list) -> None:
        """Collect datasets from code analysis.

        Args:
            datasets: List of datasets found in the code
        """
        if datasets:
            self.logger.debug(f"Adding datasets: {datasets}")
            for dataset in datasets:
                if dataset not in self._datasets:
                    self._datasets.append(dataset)
                    self.logger.debug(f"Dataset added: {dataset}")
                    license_id = dataset.get("licenses", [{}])[0].get(
                        "rawLicenseId", "Unknown"
                    )
                    categories_str = ", ".join(
                        category for category in dataset.get("categories", [])
                    )
                    self.display_info(
                        f"✅ Dataset Found: {dataset.get('title', 'Unnamed Dataset')}",
                        f"LICENSE ID: {license_id})\n"
                        f"USAGE: {categories_str}\n"
                        f"ROWS: {dataset.get('numRows')}\n"
                        f"OWNER: {dataset.get('supplier')}\n"
                        f"PURL: {dataset.get('purl')}\n"
                        f"DESCRIPTION: {dataset.get('description')}\n"
                        f"[View Dataset]({dataset.get('homepageUrl')})\n\n",
                    )

    def _handle_unapproved_models(self, unapproved_errors: list) -> None:
        """Handle warnings for unapproved models.

        Args:
            unapproved_errors: List of unapproved model errors
        """
        unapproved_errors = list(
            {error.model_id: error for error in unapproved_errors}.values()
        )
        for error in unapproved_errors:
            model_id = error.model_id
            quickscan_results = (
                self.model_analysis_service.trigger_quickscan_analysis(model_id)
            )
            if quickscan_results:
                self.display_warning(
                    f"🚫 Model not found in inventory: {model_id}",
                    f"Scanning`{model_id}` for more details...\n\n",
                )
                model_data = self.model_analysis_service.get_model_data_from_model_analysis(
                    model_id
                )
                if model_data:
                    self.logger.debug(
                        f"Adding {model_id} to list of detected models"
                    )
                    model_metadata = model_data.get("model_metadata", {})
                    self.model_session_service.add_detected_model(
                        key=model_id, model_metadata=model_metadata
                    )

                    self.logger.debug("Proceeding with risk assessment")
                    model_id_obj = ModelID(value=str(model_id))
                    self.logger.debug(
                        f"Assessing risk for model ID: {model_id_obj}"
                    )
                    risk_assessment = self.model_analysis_service.risk_assessment_service.assess_risk(
                        model_id=model_id_obj, model_data=model_data
                    )
                    self.logger.debug(
                        f"Risk assessment for model ID {model_id_obj}: {risk_assessment}"
                    )
                    findings = model_data.get(
                        "findings",
                        ["Model data not available for risk assessment"],
                    )
                    self.model_analysis_service.risk_assessment_service.enhance_with_findings(
                        risk_assessment, findings=findings
                    )
                    if risk_assessment:
                        self.display_warning(
                            f"🚨 {risk_assessment.risk_level} Risk Model Detected",
                            f"Model `{risk_assessment.model_name}` has been identified as a "
                            f"{str(risk_assessment.risk_level).upper()} risk model.\n\n"
                            f"⚠️ Needs Review\n{risk_assessment.format_findings()}",
                        )
            else:
                self.display_warning(
                    "🚫 Unapproved Model Detected",
                    str(error)
                    if isinstance(error, str)
                    else f"Model `{model_id}` is not approved for use.",
                )

    def _display_risk_warnings(
        self, risk_assessments: list[ModelRiskAssessment]
    ) -> None:
        """Display warnings for high-risk models.

        Args:
            risk_assessments: List of risk assessment results
        """
        # should not display duplicate for model_id
        risk_assessments = list(
            {
                assessment.model_id: assessment
                for assessment in risk_assessments
            }.values()
        )
        for assessment in risk_assessments:
            if assessment.is_high_risk:
                self.display_warning(
                    f"🚨 {assessment.risk_level} Risk Model Detected",
                    f"Model `{assessment.model_id}` found in the inventory.\n"
                    f"Model `{assessment.model_id}` has been identified as a "
                    f"{str(assessment.risk_level).upper()} risk model.\n\n"
                    f"⚠️ Needs Review\n{assessment.format_findings()}",
                )
            if not assessment.is_high_risk and assessment.in_inventory:
                self.logger.debug(
                    f"Adding model {assessment.model_id} to detected models"
                )
                self.model_session_service.add_detected_model(
                    key=assessment.model_id.value,
                    model_metadata=ModelMetadata(
                        name=assessment.model_id.name or "Unknown",
                        version="Unknown",
                        supplier=assessment.model_id.organization,
                        supplier_country="Unknown",
                    ),
                )
                self.display_info(
                    f"✅ Model `{assessment.model_id}` found in the inventory.\n",
                    f"Model `{assessment.model_id}` is not considered high risk.\n\n",
                )

    @staticmethod
    def _get_custom_model_inventory_url(
        model_id: str, api_uri: str | None
    ) -> str:
        """Get custom model inventory URL based on API URI."""
        if not api_uri:
            return ""
        if "development" in api_uri:
            return f"https://app.development.manifestcyber.dev/ai-explorer/model/{model_id}"
        elif "local" in api_uri:
            return f"http://local.manifestcyber.com:3000/ai-explorer/model/{model_id}"
        else:
            return f"https://app.manifestcyber.com/ai-explorer/model/{model_id}"

    @staticmethod
    def _markdown_links_to_html(text: str) -> str:
        import re

        """Convert Markdown links to HTML anchor tags."""
        return re.sub(
            r"\[([^\]]+)\]\(([^)]+)\)",
            r'<strong><a href="\2" target="_blank">\1</a></strong>',
            text,
        )
