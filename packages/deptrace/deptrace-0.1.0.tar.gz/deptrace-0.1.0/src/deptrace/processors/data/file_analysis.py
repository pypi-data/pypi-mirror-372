import ast
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Optional
from deptrace.visitors.data.scope_info import ScopeInfo
from deptrace.visitors.data.scope_name import ScopeName


@dataclass
class FileAnalysis:
    """Contains the analysis results for a Python source file.

    Attributes:
        abs_file_path: The path to the analyzed file
        scopes: Dictionary mapping scope names to their ScopeInfo
        ast_tree: AST of the analyzed file
    """

    abs_file_path: Path
    scopes: Dict[ScopeName, ScopeInfo]
    ast_tree: ast.Module

    def get_scope_by_filter(self, scope_filter: str) -> Optional[ScopeInfo]:
        """Get a specific scope by its fully qualified name.

        Args:
            scope_filter: The fully qualified scope name (e.g. "<module>.outer.Inner.method")

        Returns:
            The ScopeInfo for the requested scope if found, None otherwise
        """
        return self.scopes.get(ScopeName(scope_filter))
