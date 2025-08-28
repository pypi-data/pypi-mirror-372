import ast
from dataclasses import dataclass
from typing import Optional, get_args
from .scope_name import ScopeName
from .scope_node import ScopeNode
from .scope_type import ScopeType


@dataclass
class ScopeInfo:
    """Information about a scope in Python code.

    A scope is a region of code where names (variables, functions, etc.) are valid.
    This could be a module, class, function, or comprehension scope.

    Attributes:
        name: The fully qualified name of the scope (e.g. "<module>.class.function")
        node: The AST node that defines this scope
        type: The type of scope (module, class, function, etc.)
        parent: The name of the parent scope, if any
    """

    name: ScopeName
    node: ScopeNode
    type: ScopeType
    parent: Optional[ScopeName] = None

    def __post_init__(self) -> None:
        """Validate scope information after initialization."""
        valid_types = get_args(ScopeType)
        if self.type not in valid_types:
            raise TypeError(
                f"Invalid scope type: {self.type}. "
                f"Must be one of: {', '.join(valid_types)}"
            )

        node_type_mapping = {
            "module": ast.Module,
            "class": ast.ClassDef,
            "function": ast.FunctionDef,
            "async_function": ast.AsyncFunctionDef,
            "lambda": ast.Lambda,
            "listcomp": ast.ListComp,
            "setcomp": ast.SetComp,
            "dictcomp": ast.DictComp,
            "genexpr": ast.GeneratorExp,
            "match": ast.Match,
        }

        expected_type = node_type_mapping.get(self.type)
        if expected_type and not isinstance(self.node, expected_type):
            raise TypeError(
                f"Invalid node type for scope type '{self.type}'. "
                f"Expected {expected_type.__name__}, got {type(self.node).__name__}"
            )

        if not self.name:
            raise ValueError("Scope name cannot be empty")

        if self.type == "module" and not self.name.is_module:
            raise ValueError("Module scope must be named '<module>'")

        if self.type != "module" and not self.parent:
            raise ValueError(f"Non-module scope '{self.name}' must have a parent scope")
