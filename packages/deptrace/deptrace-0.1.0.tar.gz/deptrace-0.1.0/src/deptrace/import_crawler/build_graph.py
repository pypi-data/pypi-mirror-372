from pathlib import Path
from deptrace.logging import get_logger
from .file_dependency_graph import FileDependencyGraph
from .parse_file import parse_file
from .process_imports import process_imports
logger = get_logger(__name__)


def build_graph(
    *,
    file_path: Path,
    graph: FileDependencyGraph,
    visited_paths: set[Path],
    stdlib_paths: set[Path],
) -> FileDependencyGraph:
    """
    Recursively builds the import graph.
    If no file path is provided, uses the root file.
    Returns the dependency graph for convenience.

    Args:
        file_path: The absolute path to the file to crawl

    Returns:
        The dependency graph
    """

    if file_path in visited_paths or not file_path.suffix == ".py":
        logger.debug(f"Skipping file: {file_path.name}")
        return graph

    logger.info(f"Building graph for {file_path.name}")

    visited_paths.add(file_path)

    tree = parse_file(file_path)

    if tree is None:
        logger.warning(f"Failed to parse {file_path.name}")
        return graph

    module_dir = file_path.parent

    graph = process_imports(
        tree=tree,
        file_path=file_path,
        module_dir=module_dir,
        graph=graph,
        stdlib_paths=stdlib_paths,
        visited_paths=visited_paths,
    )

    return graph
