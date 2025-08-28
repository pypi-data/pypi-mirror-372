from typing import Dict, Optional, List, Any
from deptrace.visitors.data.scope_info import ScopeInfo
from deptrace.processors.data.file_analysis import FileAnalysis
from deptrace.visitors.data.scope_name import ScopeName
from deptrace.visitors.data.assignment_data import AssignmentData


def format_analysis(
    *,
    analysis: FileAnalysis,
    scope_filter: Optional[str] = None,
    assignments: Optional[List[AssignmentData]] = None,
) -> Dict[str, Any]:
    """Convert the analysis to a dictionary containing the processed scopes and assignments.

    This function handles the conversion from visitor data structures to simple
    dictionaries that can be consumed by the formatters layer.

    Args:
        analysis: The analysis to convert
        scope_filter: Optional fully qualified scope name to filter the output
        assignments: List of assignments found in the analyzed file

    Returns:
        A dictionary containing the processed scopes and assignments
    """
    if assignments is None:
        assignments = []

    result: Dict[str, Any] = {"scopes": {}, "assignments": []}

    def process_scope(
        scope_name: ScopeName, scopes: Dict[ScopeName, ScopeInfo]
    ) -> Dict[str, Any]:
        """Process a scope and its children into a dict structure."""
        scope_info = scopes[scope_name]
        scope_dict: Dict[str, Any] = {
            "name": str(scope_name),
            "type": scope_info.type,
            "children": [],
        }

        children = [
            name for name, info in scopes.items() if str(info.parent) == str(scope_name)
        ]
        for child in sorted(children, key=lambda x: str(x)):
            scope_dict["children"].append(process_scope(child, scopes))

        return scope_dict

    # Process scopes based on filter
    if scope_filter:
        if scope_filter not in [str(name) for name in analysis.scopes.keys()]:
            result["error"] = f"Scope '{scope_filter}' not found"
        else:
            result["scopes"] = process_scope(ScopeName(scope_filter), analysis.scopes)
    else:
        result["scopes"] = process_scope(ScopeName("<module>"), analysis.scopes)

    # Process assignments
    if assignments:
        type_indicators = {
            "basic": "=",
            "augmented": "+=/-=/*=/etc",
            "annotated": ": type =",
        }

        for assignment in sorted(assignments, key=lambda x: x.name):
            result["assignments"].append(
                {
                    "name": assignment.name,
                    "type": assignment.type,
                    "operator": type_indicators.get(assignment.type, "unknown"),
                }
            )

    return result
