import sysconfig
from typing import Set
from pathlib import Path
from deptrace.logging import get_logger

logger = get_logger(__name__)


def find_project_site_packages(project_root: Path) -> Set[Path]:
    """
    Find site-packages directories associated with the project being analyzed.
    Searches from project root upwards until finding Python environment markers.

    Args:
        project_root: Root directory of the project to analyze

    Returns:
        Set of absolute paths to site-packages directories
    """
    site_packages = set()
    current_dir = project_root.resolve()

    while True:
        # Virtual environment markers
        venv_markers = [
            current_dir / "venv",
            current_dir / ".venv",
            current_dir / "env",
            current_dir / ".env",
        ]

        # Project markers
        project_markers = [
            current_dir / "pyproject.toml",
            current_dir / "requirements.txt",
        ]

        # Check virtual environment site-packages
        for venv_dir in venv_markers:
            if venv_dir.is_dir():
                # Look for lib/pythonX.Y/site-packages
                lib_dir = venv_dir / "lib"
                if lib_dir.is_dir():
                    for item in lib_dir.iterdir():
                        if item.name.startswith("python"):
                            site_pkg = item / "site-packages"
                            if site_pkg.is_dir():
                                site_packages.add(site_pkg.resolve())

        # If we found any project markers, stop searching upward
        if any(marker.exists() for marker in project_markers):
            break

        # Move up one directory
        parent_dir = current_dir.parent
        if parent_dir == current_dir:  # Reached root directory
            break
        current_dir = parent_dir

    # If no environment-specific paths found, fall back to system site-packages
    if not site_packages:
        paths = sysconfig.get_paths()
        site_packages = {
            Path(p).resolve() for p in paths.values() if "site-packages" in p
        }

    logger.debug(f"Found site-packages paths: {site_packages}")
    return site_packages