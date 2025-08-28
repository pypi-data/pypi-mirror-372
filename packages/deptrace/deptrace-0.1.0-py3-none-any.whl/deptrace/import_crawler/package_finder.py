from pathlib import Path
from deptrace.logging import get_logger

logger = get_logger(__name__)


def find_outermost_package_root(
    start_dir: Path
) -> Path:
    """
    Recursively searches for the outermost Python package/module directory.
    A directory is considered a Python package/module if it:
        1. Contains an __init__.py file, or
        2. Contains any .py files

    Args:
        start_dir: The starting directory path to begin the search from

    Returns:
        The path to the outermost Python package/module directory
    """

    logger.debug(f"Finding outermost package root starting from: {start_dir}")

    def is_python_dir(dir_path: Path) -> bool:
        # Check for __init__.py
        if (dir_path / "__init__.py").exists():
            return True

        # Check for any .py files
        for file in dir_path.iterdir():
            if file.is_file() and file.suffix == ".py":
                return True
        return False

    current_path = start_dir.resolve()
    last_valid_path = current_path

    while True:
        parent_path = current_path.parent

        # Stop if we reached the root directory
        if parent_path == current_path:
            break

        try:
            if is_python_dir(parent_path):
                last_valid_path = parent_path
                current_path = parent_path
            else:
                break
        except (PermissionError, FileNotFoundError):
            # Stop if we can't access the directory
            break

    logger.debug(f"Found outermost root: {last_valid_path}")
    return last_valid_path