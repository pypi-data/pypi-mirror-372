from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class ScopeName:
    """Represents a fully qualified scope name in Python code.

    A scope name is a dot-separated path representing the nesting of scopes,
    starting from the module scope. For example:
    - "<module>"
    - "<module>.MyClass"
    - "<module>.outer.Inner.method"
    - "<module>.function.<lambda_line_1>"

    Attributes:
        value: The full scope name string
    """

    value: str

    def __post_init__(self) -> None:
        """Validate the scope name format."""
        if not self.value:
            raise ValueError("Scope name cannot be empty")

        # Allow "<module>" and names that start with "<module>."
        # Any other validation is handled by ScopeInfo
        if self.value != "<module>" and "." in self.value and not self.value.startswith("<module>."):
            raise ValueError("Hierarchical scope names must start with '<module>'")

    @property
    def is_module(self) -> bool:
        """Whether this is the module scope."""
        return self.value == "<module>"

    @property
    def parent(self) -> Optional["ScopeName"]:
        """Get the parent scope name, if any."""
        if self.is_module:
            return None

        last_dot = self.value.rfind(".")
        if last_dot == -1:
            return None

        parent_str = self.value[:last_dot]
        if parent_str == "<module":  # Handle the case of direct module children
            parent_str = "<module>"
        return ScopeName(parent_str)

    @property
    def local_name(self) -> str:
        """Get the local name of this scope (without parent path)."""
        return self.value.rsplit(".", 1)[-1]

    def child(self, name: str) -> "ScopeName":
        """Create a child scope name under this scope.

        Args:
            name: The local name of the child scope

        Returns:
            A new ScopeName representing the child scope
        """
        return ScopeName(f"{self.value}.{name}")

    def __str__(self) -> str:
        return self.value

    def __bool__(self) -> bool:
        """Return True if the scope name is not empty."""
        return bool(self.value)