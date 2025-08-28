import ast
from pathlib import Path
from typing import Optional


def parse_file(file_path: Path) -> Optional[ast.AST]:
    """
    Parses a Python file and returns its AST.
    Returns None if the file cannot be parsed or found.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return ast.parse(f.read(), filename=file_path)
    except (SyntaxError, FileNotFoundError):
        return None