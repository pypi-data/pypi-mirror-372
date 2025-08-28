import ast
from pathlib import Path
from deptrace.tools import parse_file
from deptrace.visitors import ScopeVisitor
from deptrace.processors.data.file_analysis import FileAnalysis


def process_file(abs_file_path: Path, depth: int) -> FileAnalysis:
    """
    Analyze a Python file by parsing it into an AST and identifying scopes.

    Args:
        file_path: Path to the Python file to analyze
        depth: Maximum depth to traverse the AST (not implemented yet)

    Returns:
        FileAnalysis object containing the complete analysis results,
        including all scopes and their relationships
    """
    ast_tree: ast.Module = parse_file(abs_file_path)
    visitor = ScopeVisitor()
    visitor.visit(ast_tree)
    return FileAnalysis(abs_file_path=abs_file_path, scopes=visitor.scopes, ast_tree=ast_tree)
