import ast
from pathlib import Path
from .file_dependency_graph import FileDependencyGraph
from .resolve_import import resolve_import
from deptrace.logging import get_logger
logger = get_logger(__name__)

def process_imports(
    tree: ast.AST,
    file_path: Path,
    module_dir: Path,
    graph: FileDependencyGraph,
    stdlib_paths: set[Path],
    visited_paths: set[Path],
) -> FileDependencyGraph:
    """Process import statements in the AST and add them to the graph."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                alias_name: str = alias.name
                resolve_import(
                    module_name_str=alias_name,
                    current_file_path=file_path,
                    search_dir=module_dir,
                    graph=graph,
                    stdlib_paths=stdlib_paths,
                    visited_paths=visited_paths,
                )
        elif isinstance(node, ast.ImportFrom):
            if isinstance(node.module, str):
                module_name: str = node.module
                if module_name:
                    resolve_import(
                        module_name_str=module_name,
                        current_file_path=file_path,
                        search_dir=module_dir,
                        graph=graph,
                        stdlib_paths=stdlib_paths,
                        visited_paths=visited_paths,
                    )
    return graph
