import os
from typing import Optional
from .is_local_module import is_local_module


def find_local_module(
    module_name: str, search_dir: str, stdlib_paths: list[str], project_root: str
) -> Optional[str]:
    """
    Attempts to find a module relative to the current directory.
    Returns the path if found and is a local module, None otherwise.

    Args:
        module_name: Name of the module to find (can be dotted)
        search_dir: Directory to start searching from
        stdlib_paths: List of standard library paths to exclude
        project_root: Root directory of the project
    """
    if not module_name:
        return None

    parts = module_name.split(".")
    potential_paths = [
        os.path.join(search_dir, *parts) + ".py",
        os.path.join(search_dir, *parts, "__init__.py"),
    ]

    for path in potential_paths:
        if os.path.exists(path) and is_local_module(path, stdlib_paths, project_root):
            return path

    return None
