import ast
from typing import Union


AssignmentNode = Union[
    ast.Assign,  # Basic assignment (x = 1)
    ast.AugAssign,  # Augmented assignment (x += 1)
    ast.AnnAssign,  # Annotated assignment (x: int = 1)
]
