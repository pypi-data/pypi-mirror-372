import ast
from pathlib import Path


def parse_file(abs_file_path: Path) -> ast.Module:
    """
    Parse a Python file into an AST.

    Args:
        abs_file_path: Absolute path to the Python file to parse

    Returns:
        The AST of the parsed file
    """
    if not abs_file_path.exists():
        raise FileNotFoundError(f"File not found: {abs_file_path}")

    with open(abs_file_path, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source, filename=abs_file_path)
        return tree
    except SyntaxError as e:
        raise SyntaxError(f"Failed to parse {abs_file_path}: {str(e)}")
