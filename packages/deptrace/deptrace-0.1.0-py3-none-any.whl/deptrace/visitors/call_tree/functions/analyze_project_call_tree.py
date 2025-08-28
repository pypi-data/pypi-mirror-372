from pathlib import Path
from typing import Any

from deptrace.tools.parse_file import parse_file
from deptrace.visitors.call_tree.functions.analyze_call_tree import analyze_call_tree


def discover_python_files(project_path: Path) -> list[Path]:
    """Discover all Python files in a project directory."""
    python_files = []
    for file_path in project_path.rglob("*.py"):
        # Skip __pycache__ directories
        if "__pycache__" not in str(file_path):
            python_files.append(file_path)
    return python_files


def analyze_project_call_tree(
    project_path: str, target_function_name: str
) -> dict[str, Any]:
    """
    Analyze Python project to find all calls to a target function across files.

    Args:
        project_path: Path to the project directory
        target_function_name: Name of the target function to trace

    Returns:
        A dictionary with the call tree structure containing:
        - target_function: The name of the target function
        - direct_callers: List of functions that directly call the target
    """
    project_root = Path(project_path)

    # Step 1: Discover all Python files in the project
    python_files = discover_python_files(project_root)

    # Step 2: Parse all files and build a map of ALL function calls
    all_calls = {}  # Maps function names to lists of functions they call

    for file_path in python_files:
        # Parse the file
        tree = parse_file(file_path)
        if tree is None:
            continue

        # Get source code for analyze_call_tree
        source_code = file_path.read_text()

        # Analyze ALL function calls in this file (not just target)
        # For now, we'll analyze each function individually
        # TODO: This needs to be more comprehensive

    # Step 3: Find direct calls to target
    all_direct_callers = []

    for file_path in python_files:
        # Parse the file
        tree = parse_file(file_path)
        if tree is None:
            continue

        # Get source code for analyze_call_tree
        source_code = file_path.read_text()

        # Analyze this file for calls to target function
        file_result = analyze_call_tree(source_code, target_function_name)

        # Add file information to each caller
        for caller in file_result["direct_callers"]:
            caller["file"] = str(file_path.relative_to(project_root))
            all_direct_callers.append(caller)

    # Step 4: Build recursive caller relationships
    def find_callers_recursive(func_name: str, visited: set = None) -> list:
        """Recursively find all callers of a function."""
        if visited is None:
            visited = set()

        if func_name in visited:
            return []

        visited.add(func_name)

        callers = []
        for file_path in python_files:
            source_code = file_path.read_text()
            result = analyze_call_tree(source_code, func_name)

            for caller in result["direct_callers"]:
                caller["file"] = str(file_path.relative_to(project_root))
                # Recursively find who calls this caller
                caller["callers"] = find_callers_recursive(
                    caller["name"], visited.copy()
                )
                callers.append(caller)

        return callers

    # Apply recursive caller finding to each direct caller
    for direct_caller in all_direct_callers:
        direct_caller["callers"] = find_callers_recursive(direct_caller["name"])

    return {
        "target_function": target_function_name,
        "direct_callers": all_direct_callers,
    }
