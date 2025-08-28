from dataclasses import dataclass
from typing import get_args
from .assignment_node import AssignmentNode
from .assignment_type import AssignmentType
from .scope_name import ScopeName


@dataclass
class AssignmentData:
    """Represents a variable assignment in Python code.

    Attributes:
        name: The name of the variable being assigned
        node: The AST node representing the assignment (Assign, AugAssign, or AnnAssign)
        type: The type of assignment (basic, augmented, annotated, etc.)
        scope_name: The fully qualified name of the scope containing this assignment
    """

    name: str
    node: AssignmentNode
    type: AssignmentType
    scope_name: ScopeName

    def __post_init__(self) -> None:
        """Validate the assignment type after initialization."""
        valid_types = get_args(AssignmentType)
        if self.type not in valid_types:
            raise TypeError(
                f"Invalid assignment type: {self.type}. "
                f"Must be one of: {', '.join(valid_types)}"
            )
