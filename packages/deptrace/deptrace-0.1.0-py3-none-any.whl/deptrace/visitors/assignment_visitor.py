import ast
from ast import Name, Attribute, Subscript
from typing import List
from deptrace.visitors.data.scope_name import ScopeName
from deptrace.visitors.data.assignment_data import AssignmentData


class AssignmentVisitor(ast.NodeVisitor):
    """AST visitor that collects variable assignments within a scope."""

    def __init__(self, scope_name: ScopeName) -> None:
        self.assignments: List[AssignmentData] = []
        self.scope_name = scope_name

    def visit_Assign(self, node: ast.Assign) -> None:
        """Basic assignments like 'x = 1'."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.assignments.append(
                    AssignmentData(
                        name=target.id,
                        node=node,
                        type="basic",
                        scope_name=self.scope_name,
                    )
                )
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        """Augmented assignments like 'x += 1'."""
        target: Name | Attribute | Subscript = node.target
        if isinstance(target, Name):
            self.assignments.append(
                AssignmentData(
                    name=target.id,
                    node=node,
                    type="augmented",
                    scope_name=self.scope_name,
                )
            )
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Annotated assignments like 'x: int = 1'."""
        if isinstance(target := node.target, ast.Name):
            self.assignments.append(
                AssignmentData(
                    name=target.id,
                    node=node,
                    type="annotated",
                    scope_name=self.scope_name,
                )
            )
        self.generic_visit(node)
