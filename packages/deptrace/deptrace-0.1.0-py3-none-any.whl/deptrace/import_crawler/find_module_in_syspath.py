import sys
from importlib.util import find_spec
from pathlib import Path
from typing import Optional
from deptrace.logging import get_logger
from .is_source_layout_package import is_src_layout_project

logger = get_logger(__name__)


def find_module_in_syspath(
    *,
    module_name: str,
    parent_path: Path,
    stdlib_paths: set[Path],
) -> Optional[Path]:
    """
    Attempts to find the module through sys.path.
    Returns the path if found and is a local module, None otherwise.
    For src-layout projects, temporarily adds the src parent directory to sys.path.
    """
    # Save the original sys.path to restore it later
    original_sys_path: list[str] = sys.path.copy()

    # Calculate src project root once if needed
    src_root: Path | None = None
    if is_src_layout_project(parent_path):
        path_parts: tuple[str, ...] = parent_path.parts
        if "src" in path_parts:
            src_index = path_parts.index("src")
            # The project root should be the directory containing src/
            src_root = Path(*path_parts[:src_index])

    try:
        # Add src project root to sys.path if found
        if src_root:
            log_str = f"Adding src project root to sys.path: {src_root}"
            logger.debug(log_str)
            sys.path.insert(0, str(src_root))

        # Look for the module using importlib
        spec = find_spec(module_name)
        if spec and spec.origin:
            # Filter out compiled modules and non-local modules
            if spec.origin.endswith(".py"):
                module_path = Path(spec.origin).resolve()
                # Check if module is in standard library
                for stdlib_path in stdlib_paths:
                    if module_path.is_relative_to(stdlib_path):
                        return None
                # Check if module is within project directory or src directory
                if src_root and module_path.is_relative_to(src_root):
                    return module_path
                # Otherwise use the standard project_root check
                elif module_path.is_relative_to(parent_path):
                    return module_path
    except (ImportError, AttributeError):
        pass
    finally:
        # Restore the original sys.path
        sys.path = original_sys_path

    return None
