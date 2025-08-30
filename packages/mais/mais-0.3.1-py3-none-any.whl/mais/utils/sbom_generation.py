import os
from pathlib import Path
import re
import subprocess
import sys

from mais.utils.logger import logger


def strip_ansi_codes(text: str) -> str:
    ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
    return ansi_escape.sub("", text)


def get_binary_path() -> str:
    """Get the path to the manifest-cli binary."""
    # Get the path to the mais package
    package_dir = Path(__file__).parent.parent
    binary_path = package_dir / "bin" / "manifest-cli"

    if not binary_path.exists():
        raise FileNotFoundError(
            f"manifest-cli binary not found at {binary_path}"
        )

    # Make sure it's executable
    os.chmod(binary_path, 0o755)
    return str(binary_path)


def pip_freeze() -> list[str]:
    """
    Run 'pip freeze' or 'uv pip freeze' and save the output to a requirements file.

    Returns:
        List of installed packages as strings, each in the format 'package==version'.
    """

    # Try different methods to get installed packages
    commands = [
        ["pip", "freeze", "--no-color"],
        ["uv", "pip", "freeze", "--color", "never"],  # Try system uv pip
        [sys.executable, "-m", "pip", "freeze", "--no-color"],  # Try pip module
    ]

    last_error = None
    for cmd in commands:
        try:
            logger.debug(f"Trying to get requirements with: {' '.join(cmd)}")
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True
            )

            return result.stdout.splitlines()
        except subprocess.CalledProcessError as e:
            last_error = e
            logger.debug(f"Command {' '.join(cmd)} failed: {e.stderr}")
            continue
        except FileNotFoundError:
            logger.debug(f"Command {cmd[0]} not found")
            continue

    # If all methods failed, raise the last error
    if last_error:
        logger.error(
            "✗ Error: Could not generate requirements file. All methods failed."
        )
        logger.error(f"✗ Last error: {last_error.stderr}")
        raise last_error
    else:
        raise Exception("Could not find pip or uv to generate requirements")


def run_manifest_cli(
    args: list[str],
    input_data: str | None = None,
    cwd: str | None = None,
    api_key: str = "",
) -> subprocess.CompletedProcess:
    """Run manifest-cli with given arguments.

    Args:
        args: Command line arguments for manifest-cli
        input_data: Optional input data for stdin
        cwd: Working directory for the command

    Returns:
        subprocess.CompletedProcess with the result
    """
    binary_path = get_binary_path()
    cmd = [binary_path, *args]
    logger.debug(
        f"Manifest API Token: {api_key if api_key else 'Not provided'}"
    )

    # If cwd is specified, use it
    working_dir = cwd if cwd else None
    logger.debug(
        f"Running command: {' '.join(cmd)} in {working_dir if working_dir else 'current directory'}"
    )
    return subprocess.run(
        cmd,
        input=input_data,
        text=True,
        capture_output=True,
        env={**os.environ, "MANIFEST_API_KEY": api_key},
        cwd=working_dir,
    )
