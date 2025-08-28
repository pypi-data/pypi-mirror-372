from pathlib import Path
from typing import Optional, List
from deptrace.logging import get_logger

logger = get_logger(__name__)


def get_ancestor_paths(start_dir: Path, outer_root: Path) -> List[Path]:
    """Returns a list of all ancestor directory paths from start_dir up to outer_root."""
    paths = []
    # When you use Path.resolve(), it resolves symlinks.
    # The old implementation with os.path.abspath() doesn't do that.
    current = start_dir.absolute()
    outer_root = outer_root.absolute()

    while True:
        paths.append(current)
        if current == outer_root or len(str(current)) < len(str(outer_root)):
            break
        current = current.parent

    return paths


def find_module_in_package_hierarchy(
    module_name: str,
    start_dir: Path,
    outer_root: Path,
) -> Optional[Path]:
    """
    Searches for a module through the package hierarchy by checking each ancestor directory.

    Args:
        module_name: Name of the module to find (can be dotted)
        start_dir: Directory to start searching from
        outer_root: Outermost package root directory
    """

    logger.debug(f"Searching for {module_name} from {start_dir} up to {outer_root}")

    # Get all possible directory paths to search
    search_paths = get_ancestor_paths(start_dir, outer_root)

    # For each path, try to find the module
    for path in search_paths:
        # Try as a direct .py file
        module_file = path / f"{module_name}.py"
        if module_file.is_file():
            logger.debug(f"Found module file: {module_file}")
            return module_file

        # Try as a package
        package_init = path / module_name / "__init__.py"
        if package_init.is_file():
            logger.debug(f"Found package: {package_init}")
            return package_init

        # Try as a dotted file (for cases like views.render_html.py)
        if "." in module_name:
            module_parts = module_name.split(".")
            # Try each possible combination of dots vs directories
            for i in range(len(module_parts)):
                file_part = f"{'.'.join(module_parts[i:])}.py"
                dir_part = Path(*module_parts[:i]) if i > 0 else Path(".")
                full_path = path / dir_part / file_part
                if full_path.is_file():
                    logger.debug(f"Found dotted module: {full_path}")
                    return full_path

    logger.debug(f"Module {module_name} not found in hierarchy")
    return None
