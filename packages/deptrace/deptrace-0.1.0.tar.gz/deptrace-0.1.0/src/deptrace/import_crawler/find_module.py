from pathlib import Path
from typing import Optional
from deptrace.logging import get_logger
from .package_finder import find_outermost_package_root
from .package_searcher import find_module_in_package_hierarchy
from .is_source_layout_package import is_src_layout_project
from .find_module_in_syspath import find_module_in_syspath

logger = get_logger(__name__)


def find_module(
    *,
    module_name: str,
    search_dir: Path,
    parent_path: Path,
    stdlib_paths: set[Path],
) -> Optional[Path]:
    """
    Attempts to find the module file given its name by:
    1. Searching through the package hierarchy from current directory
    2. If we're in a src-layout project, try to find the module considering the src directory
    3. If not found locally, try finding through sys.path
    """
    # First try searching through package hierarchy
    outer_root: Path = find_outermost_package_root(search_dir)

    module_path: Path | None = find_module_in_package_hierarchy(
        module_name,
        search_dir,
        outer_root,
    )

    if module_path:
        return module_path

    # Check if we're in a src-layout project
    if is_src_layout_project(parent_path):
        logger.debug(f"Detected src layout, trying resolution for {module_name}")
        # Find the src directory in the path
        path_parts: tuple[str, ...] = parent_path.parts
        if "src" in path_parts:
            src_index = path_parts.index("src")
            # The project root should be the directory containing src/
            src_root = Path(*path_parts[:src_index])

            # Try to resolve absolute imports through the src directory
            if module_name.count(".") > 0:
                # Split the module name into package and submodule parts
                parts = module_name.split(".")
                # Try reconstructing the path based on src-layout conventions
                possible_paths: list[Path] = []

                # Try as a direct path from src directory
                src_path = src_root / "src"
                package_path = src_path.joinpath(*parts)
                possible_paths.append(package_path.with_suffix(".py"))
                possible_paths.append(package_path / "__init__.py")

                # Try with src/parts[0]/parts[1:] structure
                if len(parts) > 1:
                    package_path = src_path / parts[0]
                    submodule_path = package_path.joinpath(*parts[1:])
                    possible_paths.append(submodule_path.with_suffix(".py"))
                    possible_paths.append(submodule_path / "__init__.py")

                # Check all possible paths
                for path in possible_paths:
                    if path.exists():
                        logger.debug(f"Found module in src-layout: {path}")
                        return path

    # If not found locally, try finding through sys.path
    module_in_syspath: Path | None = find_module_in_syspath(
        module_name=module_name,
        parent_path=parent_path,
        stdlib_paths=stdlib_paths,
    )

    if module_in_syspath:
        return module_in_syspath

    return None
