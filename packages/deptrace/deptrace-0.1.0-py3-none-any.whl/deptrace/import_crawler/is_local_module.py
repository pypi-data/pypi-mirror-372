import os


def is_local_module(
    module_path: str, stdlib_paths: list[str], project_root: str
) -> bool:
    """
    Determines if a module is local to the project by checking:
    1. Not in standard library paths
    2. Within project directory
    """
    module_path = os.path.abspath(module_path)

    # Check if module is in standard library
    for stdlib_path in stdlib_paths:
        if module_path.startswith(stdlib_path):
            return False

    # Check if module is within project directory
    if not module_path.startswith(project_root):
        return False

    return True
