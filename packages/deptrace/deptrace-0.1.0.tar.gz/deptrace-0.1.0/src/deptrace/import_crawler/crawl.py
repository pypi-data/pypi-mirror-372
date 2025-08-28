import sysconfig
from pathlib import Path
from .build_graph import build_graph
from .file_dependency_graph import FileDependencyGraph
from .import_categorizer import ImportCategorizer
from .site_packages import find_project_site_packages
from typing import Dict, List
from deptrace.logging import get_logger

logger = get_logger(__name__)


def crawl(
    abs_file_path: Path,
) -> tuple[FileDependencyGraph, Dict[str, List[str]]]:
    """Crawl the import graph for the given entry file.

    Args:
        abs_file_path: The file to crawl

    Returns:
        A tuple containing:
        - FileDependencyGraph: The dependency graph of imported modules
        - dict: Unresolved imports categorized as local, system, and third-party
    """

    logger.info(f"Analyzing imports for {abs_file_path.name}")

    parent_path = abs_file_path.parent
    visited_paths: set[Path] = set()

    # Get standard library paths
    paths: Dict[str, str] = sysconfig.get_paths()

    # We use strings here because this data is always used with importlib.util.find_spec.
    stdlib_path_strs = set([p for p in paths.values()])

    stdlib_paths: set[Path] = set([Path(p) for p in paths.values()])

    site_packages_paths: set[Path] = find_project_site_packages(
        parent_path,
    )

    import_categorizer = ImportCategorizer(
        stdlib_path_strs,
        site_packages_paths,
    )

    graph = FileDependencyGraph(import_categorizer)

    graph = build_graph(
        file_path=abs_file_path,
        graph=graph,
        visited_paths=visited_paths,
        stdlib_paths=stdlib_paths,
    )

    # Get unresolved imports for JSON output
    unresolved_imports = graph.import_categorizer.get_unresolved_imports()

    return graph, unresolved_imports
