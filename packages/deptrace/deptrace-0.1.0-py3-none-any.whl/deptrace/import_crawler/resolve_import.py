from pathlib import Path
from .file_dependency_graph import FileDependencyGraph
from .file_info import FileInfo
from deptrace.logging import get_logger
from .find_module import find_module

logger = get_logger(__name__)


def resolve_import(
    *,
    module_name_str: str,
    current_file_path: Path,
    search_dir: Path,
    graph: FileDependencyGraph,
    stdlib_paths: set[Path],
    visited_paths: set[Path],
) -> None:
    """Resolves the module path and updates the graph."""
    logger.debug(f"Resolving import {module_name_str} from {current_file_path}")

    module_path = find_module(
        module_name=module_name_str,
        search_dir=search_dir,
        parent_path=current_file_path.parent,
        stdlib_paths=stdlib_paths,
    )

    if module_path:
        from .build_graph import build_graph
        current = FileInfo(current_file_path)
        module = FileInfo(module_path)
        graph.add_dependency(current, module)
        build_graph(
            file_path=module_path,
            graph=graph,
            visited_paths=visited_paths,
            stdlib_paths=stdlib_paths,
        )
    else:
        graph.import_categorizer.categorize_import(module_name_str)
        logger.debug(f"Could not resolve {module_name_str}")
