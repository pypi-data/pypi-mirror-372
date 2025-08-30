"""Module for analyzing Python AST to detect model loading patterns."""

import ast

from mais.config import get_config
from mais.utils.logger import logger


class ASTAnalyzer:
    """Analyzes Python code AST to detect ML model loading patterns."""

    def __init__(self):
        """Initialize the AST analyzer."""
        self.logger = logger
        config = get_config()
        self.watched_functions = config.watched_functions
        self.watched_classes = config.watched_classes
        self.model_related_kwargs = config.model_related_kwargs
        self.dataset_tasks = config.datasets_tasks

    def analyze_code(
        self, code: str
    ) -> tuple[dict[str, str], dict[str, str], list[ast.Call]]:
        """Analyze code and extract model loading information.

        Args:
            code: Python code to analyze

        Returns:
            Tuple of (class_aliases, variable_models, call_nodes)

        Raises:
            SyntaxError: If code has syntax errors
        """
        self.logger.debug(f"Analyzing code: {code[:50]}...")

        try:
            tree = ast.parse(code)
            self.logger.debug("Successfully parsed code with AST")
        except SyntaxError as e:
            self.logger.error(f"Syntax error in code: {e}")
            raise

        class_aliases = self._find_class_aliases(tree)
        variable_models = self._find_variable_model_assignments(tree)
        call_nodes = [
            node for node in ast.walk(tree) if isinstance(node, ast.Call)
        ]

        return class_aliases, variable_models, call_nodes

    @staticmethod
    def extract_string_value(node: ast.AST) -> str | None:
        """Extract string value from an AST node.

        Args:
            node: AST node to extract from

        Returns:
            String value or None if not a string
        """
        if isinstance(node, ast.Str):  # Python < 3.8
            return node.s
        elif isinstance(node, ast.Name):
            return f"<variable: {node.id}>"
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return None

    @staticmethod
    def extract_function_path(node: ast.AST) -> str | None:
        """Extract function path from an AST node.

        Args:
            node: AST node to extract from

        Returns:
            Function path as string or None
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            path = []
            attr: ast.expr = node
            while isinstance(attr, ast.Attribute):
                path.append(attr.attr)
                attr = attr.value
            if isinstance(attr, ast.Name):
                path.append(attr.id)
            path.reverse()
            return ".".join(path)
        return None

    def function_matches_watched(self, func_path: str) -> bool:
        """Check if a function path matches any watched patterns.

        Args:
            func_path: Function path to check

        Returns:
            True if function is watched
        """
        if not func_path:
            return False

        self.logger.debug(f"Checking if function matches watched: {func_path}")

        # Exact match
        if func_path in self.watched_functions:
            self.logger.debug(
                f"Found exact match for function {func_path} in watched list"
            )
            return True

        parts = func_path.split(".")

        # Direct class match
        if len(parts) == 1 and parts[0] in self.watched_classes:
            self.logger.debug(f"Found direct function match for {func_path}")
            return True

        # Class.from_pretrained pattern
        if (
            len(parts) >= 2
            and parts[-1] == "from_pretrained"
            and parts[-2] in self.watched_classes
        ):
            self.logger.debug(
                f"Found class match for function {func_path} with class {parts[-2]}"
            )
            return True

        # Partial match for module.class.method patterns
        for watched in self.watched_functions:
            watched_parts = watched.split(".")
            if (
                len(watched_parts) >= 2
                and len(parts) >= 2
                and watched_parts[-2:] == parts[-2:]
            ):
                self.logger.debug(
                    f"Found partial match for function {func_path} with {watched}"
                )
                return True

        self.logger.debug(f"No match found for function: {func_path}")
        return False

    def resolve_function_path(
        self, func_node: ast.AST, class_aliases: dict[str, str]
    ) -> tuple[str | None, bool]:
        """Resolve function path considering aliases.

        Args:
            func_node: Function AST node
            class_aliases: Dictionary of class aliases

        Returns:
            Tuple of (function_path, is_alias_match)
        """
        func_path = self.extract_function_path(func_node)
        is_alias_match = False

        if func_path:
            parts = func_path.split(".")

            # Check for aliased class methods
            if (
                len(parts) >= 2
                and parts[-1] == "from_pretrained"
                and parts[-2] in class_aliases
            ):
                original_class = class_aliases[parts[-2]]
                self.logger.debug(
                    f"Found aliased class method: {func_path} is alias for {original_class}.from_pretrained"
                )
                is_alias_match = True

            # Check for aliased functions
            elif len(parts) == 1 and parts[0] in class_aliases:
                original_func = class_aliases[parts[0]]
                self.logger.debug(
                    f"Found aliased function: {func_path} is alias for {original_func}"
                )
                func_path = original_func
                is_alias_match = True

        return func_path, is_alias_match

    def extract_model_from_call(
        self, call_node: ast.Call, variable_models: dict[str, str]
    ) -> list[tuple[str, str, bool]]:
        """Extract model information from a function call.

        Args:
            call_node: Call AST node
            variable_models: Dictionary of variable model assignments

        Returns:
            List of tuples (model_name, display_name, is_variable)
        """
        models = []

        # Check positional arguments
        for arg in call_node.args:
            model_name = self.extract_string_value(arg)
            if model_name and not model_name.startswith("<variable:"):
                models.append((model_name, model_name, False))
            elif isinstance(arg, ast.Name) and arg.id in variable_models:
                actual_model = variable_models[arg.id]
                models.append(
                    (actual_model, f"{arg.id} = {actual_model}", True)
                )

        # Check keyword arguments
        for keyword_arg in call_node.keywords:
            if keyword_arg.arg in self.model_related_kwargs:
                model_name = self.extract_string_value(keyword_arg.value)
                if model_name and not model_name.startswith("<variable:"):
                    models.append((model_name, model_name, False))
                elif (
                    isinstance(keyword_arg.value, ast.Name)
                    and keyword_arg.value.id in variable_models
                ):
                    actual_model = variable_models[keyword_arg.value.id]
                    display_name = f"{keyword_arg.arg}={keyword_arg.value.id} = {actual_model}"
                    models.append((actual_model, display_name, True))

        return models

    def _get_croissant_metadata_from_dataset(
        self, dataset_name: str
    ) -> dict[str, str]:
        import requests

        API_URL = (
            f"https://huggingface.co/api/datasets/{dataset_name}/croissant"
        )

        def query():
            response = requests.get(API_URL)
            return response.json()

        data = query()
        return data

    def _parse_croissant_metadata(self, metadata: dict, dataset_name) -> dict:
        """Parse Croissant metadata into a structured format.

        Args:
            metadata: Raw metadata dictionary

        Returns:
            Parsed metadata dictionary
        """
        import re

        # Assume `metadata` is the dictionary provided in your example
        homepage = metadata.get(
            "url", f"https://huggingface.co/datasets/{dataset_name}"
        )
        purl = metadata.get("purl", f"pkg:huggingface/{dataset_name}")
        purl_without_revision = metadata.get(
            "purlWithoutRevision", f"pkg:huggingface/{dataset_name}"
        )
        # Supplier extraction: from 'creator'->'name', fallback to 'supplier', fallback to 'Hugging Face'
        supplier = (
            metadata.get("creator", {}).get("name")
            if isinstance(metadata.get("creator"), dict)
            and "name" in metadata.get("creator", {})
            else metadata.get("supplier", "Hugging Face")
        )

        # Extract region/country from keywords (look for 'Region: <country>')
        def extract_region(keywords):
            for kw in keywords:
                match = re.search(r"Region:\s*([A-Za-z\s]+)", kw)
                if match:
                    return match.group(1).strip()
            return "Unknown"

        keywords = metadata.get("keywords", [])
        supplier_country = extract_region(keywords)
        categories = [
            keyword for keyword in keywords if keyword in self.dataset_tasks
        ]
        description = metadata.get("description", "")

        license = metadata.get("license", "")
        self.logger.debug(f"License found: {license}")
        raw_license_id = license
        if "http" in license and license.endswith("/"):
            # Handle case where license is a URL ending with a slash
            raw_license_id = (
                license.split("/")[-2].upper()
                if len(license.split("/")) > 1
                else license
            )
        elif "http" in license:
            # Handle case where license is a URL but not ending with a slash
            # This assumes the last part of the URL is the license ID
            raw_license_id = license.split("/")[-1].upper()
        self.logger.debug(f"Raw license ID: {raw_license_id}")
        if not raw_license_id:
            raw_license_id = "UNKNOWN"
        licenses = [{"rawLicenseId": raw_license_id}]
        parsed_metadata = {
            "title": dataset_name,
            "categories": categories,
            "purl": purl,
            "purlWithoutRevision": purl_without_revision,
            "homepageUrl": homepage,
            "supplier": supplier,
            "supplierCountryOfOrigin": supplier_country,
            "description": f"""{description}""",
            "licenses": licenses,
        }
        return parsed_metadata

    def _get_size_from_dataset(self, dataset_name: str) -> tuple[int, int]:
        """Get size in bytes of a dataset from Hugging Face.

        Args:
            dataset_name: Name of the dataset

        Returns:
            Size in bytes or 0 if not found
        """
        import requests

        API_URL = f"https://datasets-server.huggingface.co/size?dataset={dataset_name}"

        def query():
            response = requests.get(API_URL)
            return response.json()

        data = query()
        num_rows = data.get("size", {}).get("dataset", {}).get("num_rows", 0)
        num_bytes_memory = (
            data.get("size", {}).get("dataset", {}).get("num_bytes_memory", 0)
        )
        return num_rows, num_bytes_memory

    def extract_dataset(self, code: str) -> list[dict]:
        """Extract dataset loading calls from code.

        Args:
            code: Python code to analyze

        Returns:
            List of dicts with dataset loading info
        """
        self.logger.debug(f"Extracting datasets from code: {code[:50]}...")
        try:
            tree = ast.parse(code)
            self.logger.debug(
                "Successfully parsed code with AST for dataset extraction"
            )
        except SyntaxError as e:
            self.logger.error(f"Syntax error in code: {e}")
            raise

        dataset_aliases = self._find_dataset_aliases(tree)
        self.logger.debug(f"Dataset aliases found: {dataset_aliases}")

        datasets_found = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_path = self.extract_function_path(node.func)
                if func_path in dataset_aliases:
                    self.logger.debug(
                        f"Found dataset loading call: {func_path}"
                    )
                    # Extract dataset name from first positional argument
                    if node.args:
                        dataset_name = self.extract_string_value(node.args[0])
                        if dataset_name:
                            dataset_info = {}
                            metadata = (
                                self._get_croissant_metadata_from_dataset(
                                    dataset_name
                                )
                            )
                            if metadata:
                                parsed_metadata = (
                                    self._parse_croissant_metadata(
                                        metadata, dataset_name
                                    )
                                )
                                num_rows, num_bytes_memory = (
                                    self._get_size_from_dataset(dataset_name)
                                )
                                dataset_info = {
                                    **parsed_metadata,
                                    "numRows": num_rows,
                                    "numBytesMemory": num_bytes_memory,
                                }
                                datasets_found.append(dataset_info)
                                self.logger.debug(
                                    f"Extracted dataset info: {dataset_info}"
                                )
                                self.logger.debug(
                                    f"Extracted dataset: {dataset_name}"
                                )
                        elif isinstance(node.args[0], ast.Name):
                            dataset_name = node.args[0].id
                            if dataset_name:
                                dataset_info = {}
                                metadata = (
                                    self._get_croissant_metadata_from_dataset(
                                        dataset_name
                                    )
                                )
                                if metadata:
                                    parsed_metadata = (
                                        self._parse_croissant_metadata(
                                            metadata, dataset_name
                                        )
                                    )
                                    num_rows, num_bytes_memory = (
                                        self._get_size_from_dataset(
                                            dataset_name
                                        )
                                    )
                                    dataset_info = {
                                        **parsed_metadata,
                                        "numRows": num_rows,
                                        "numBytesMemory": num_bytes_memory,
                                    }
                                    datasets_found.append(dataset_info)
        return datasets_found

    def _find_class_aliases(self, tree: ast.AST) -> dict[str, str]:
        """Find aliases for watched classes in imports.

        Args:
            tree: AST tree to analyze

        Returns:
            Dictionary mapping aliases to original class names
        """
        class_aliases = {}

        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ImportFrom)
                and node.module == "transformers"
            ):
                for alias in node.names:
                    if alias.name in self.watched_classes and alias.asname:
                        self.logger.debug(
                            f"Found alias for watched class: {alias.name} as {alias.asname}"
                        )
                        class_aliases[alias.asname] = alias.name

        return class_aliases

    def _find_variable_model_assignments(self, tree: ast.AST) -> dict[str, str]:
        """Find variable assignments that might contain model IDs.

        Args:
            tree: AST tree to analyze

        Returns:
            Dictionary mapping variable names to potential model IDs
        """
        variable_models = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id

                        # Handle direct string assignments
                        if (
                            isinstance(node.value, ast.Constant)
                            and isinstance(node.value.value, str)
                            and "/" in node.value.value
                        ):
                            var_value = node.value.value
                            self.logger.debug(
                                f"Found potential model ID assignment: {var_name} = {var_value}"
                            )
                            variable_models[var_name] = var_value

                        # Handle function/method calls that might load models
                        elif isinstance(node.value, ast.Call):
                            # Extract string arguments from the call
                            model_id = self._extract_model_from_assignment_call(
                                node.value
                            )
                            if model_id:
                                self.logger.debug(
                                    f"Found potential model ID from call: {var_name} = {model_id}"
                                )
                                variable_models[var_name] = model_id

        return variable_models

    def _find_dataset_aliases(self, tree: ast.AST) -> dict[str, str]:
        """Find aliases for load_dataset in imports from datasets.

        Args:
            tree: AST tree to analyze

        Returns:
            Dictionary mapping aliases to 'load_dataset'
        """
        dataset_aliases = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "datasets":
                for alias in node.names:
                    if alias.name == "load_dataset":
                        asname = alias.asname if alias.asname else alias.name
                        self.logger.debug(
                            f"Found alias for load_dataset: {alias.name} as {asname}"
                        )
                        dataset_aliases[asname] = "load_dataset"
        return dataset_aliases

    def _extract_model_from_assignment_call(
        self, call_node: ast.Call
    ) -> str | None:
        """Extract model ID from function calls in assignments."""
        # Check positional arguments for string constants
        for arg in call_node.args:
            if (
                isinstance(arg, ast.Constant)
                and isinstance(arg.value, str)
                and (
                    "/" in arg.value
                    or arg.value.replace("-", "").replace("_", "").isalnum()
                )
            ):
                return arg.value

        # Check keyword arguments for model-related parameters
        for keyword_arg in call_node.keywords:
            if (
                keyword_arg.arg
                in [
                    "model_name",
                    "pretrained_model_name_or_path",
                    "model",
                ]
                and isinstance(keyword_arg.value, ast.Constant)
                and isinstance(keyword_arg.value.value, str)
            ):
                return keyword_arg.value.value

        return None
