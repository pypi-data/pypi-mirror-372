from pathlib import Path


def is_src_layout_project(parent_path: Path) -> bool:
    """
    Detect if this is a src-layout project by looking for common
    markers like src/ directory and pyproject.toml
    """
    # Get the directory containing the file
    path_parts: tuple[str, ...] = parent_path.parts

    # Look for src/ in the path
    if "src" not in path_parts:
        return False

    # Find the index of 'src' in the path
    src_index = path_parts.index("src")

    # The project root should be the directory containing src/
    potential_project_root = Path(*path_parts[:src_index])

    # Check for project configuration files
    for config_file in ["pyproject.toml", "setup.py", "setup.cfg"]:
        if (potential_project_root / config_file).exists():
            return True

    return False
