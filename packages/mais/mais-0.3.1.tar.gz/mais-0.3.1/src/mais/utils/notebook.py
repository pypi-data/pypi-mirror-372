import json
from pathlib import Path

from mais.utils.logger import logger


def get_current_notebook_data() -> dict:
    import hashlib

    try:
        # Try Google Colab first
        import hashlib
        import json

        from google.colab import _message

        # Get the notebook name
        notebook_name = _message.blocking_request(
            "get_notebook_name", request="", timeout_sec=5
        )
        # Get notebook content as JSON
        notebook_json = _message.blocking_request("get_ipynb")["ipynb"]
        notebook_bytes = json.dumps(notebook_json, sort_keys=True).encode("utf-8")
        file_hash = hashlib.sha256(notebook_bytes).hexdigest()

        return {
            "name": notebook_name,
            "type": "colab",
            "hash": file_hash,
        }
    except Exception:
        # Fallback to local file search
        notebook_files = list(Path("").glob("*.ipynb"))

        if not notebook_files:
            logger.error("No notebook files found in the current directory.")
            return {}

        latest_notebook = max(notebook_files, key=lambda p: p.stat().st_mtime)
        name = latest_notebook.name

        with open(latest_notebook, "rb") as f:
            file_bytes = f.read()
            file_hash = hashlib.sha256(file_bytes).hexdigest()

        return {
            "name": name,
            "type": "file",
            "hash": file_hash,
        }


def get_notebook_code_universal():
    """Universal method to get notebook code."""

    # Method 1: Try IPython history first
    try:
        from IPython import get_ipython

        ip = get_ipython()

        if ip is not None:
            history = []
            for _session, _line_num, code in ip.history_manager.get_range():
                if (
                    code.strip()
                    and not code.startswith("%")
                    and not code.startswith("!")
                ):
                    history.append(code)

            if history:
                return "\n\n".join(history)
    except (ImportError, AttributeError, RuntimeError) as e:
        # Specific exceptions for IPython-related issues
        print(f"IPython method failed: {e}")

    # Method 2: Try to find and parse notebook file
    try:
        # Look for .ipynb files in current directory
        notebook_files = list(Path("").glob("*.ipynb"))

        if notebook_files:
            # Use the most recently modified notebook
            latest_notebook = max(notebook_files, key=lambda p: p.stat().st_mtime)

            with open(latest_notebook, encoding="utf-8") as f:
                notebook = json.load(f)

            code_cells = []
            for cell in notebook.get("cells", []):
                if cell.get("cell_type") == "code":
                    source = cell.get("source", [])
                    code = "".join(source) if isinstance(source, list) else source

                    if (
                        code.strip()
                        and not code.startswith("%")
                        and not code.startswith("!")
                    ):
                        code_cells.append(code)

            if code_cells:
                return "\n\n".join(code_cells)
    except (FileNotFoundError, json.JSONDecodeError, KeyError, OSError) as e:
        # Specific exceptions for file and JSON parsing issues
        logger.error(f"Notebook file method failed: {e}")

    raise RuntimeError("Could not extract notebook code")


def save_all_code_to_temp(path: str = "./") -> str:
    """Save all notebook code to a temporary file."""
    code = get_notebook_code_universal()
    filename = "notebook_code.py"
    file_path = Path(path) / filename
    with open(file_path, "w") as f:
        f.write(code)
        return filename
