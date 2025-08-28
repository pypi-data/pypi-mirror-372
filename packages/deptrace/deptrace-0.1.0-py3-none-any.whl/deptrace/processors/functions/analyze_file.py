from pathlib import Path
from typing import Dict, Any, List
from deptrace.processors.process_file import process_file
from deptrace.processors.data.file_analysis import FileAnalysis
from deptrace.visitors.data.scope_info import ScopeInfo
from deptrace.visitors.data.scope_name import ScopeName
from deptrace.visitors.data.assignment_data import AssignmentData
from deptrace.processors.process_scope import process_scope
from deptrace.import_crawler.crawl import crawl
from deptrace.tools.convert_to_abs_path import convert_to_abs_path


def analyze_file(
    file_path: str | Path, depth: int = 4, scope_filter: str | None = None
) -> Dict[str, Any]:
    """Analyze a Python file and return raw analysis results.

    Args:
        file_path: Path to the Python file to analyze
        depth: Depth of the analysis
        scope_filter: Optional scope name to filter the output

    Returns:
        Dictionary containing raw analysis results with keys:
        - file_analysis: FileAnalysis object
        - assignments: List of AssignmentData objects
        - scope_filter: The scope filter used
        - graph: dependency graph
        - unresolved_imports: unresolved imports
    """
    abs_file_path: Path = convert_to_abs_path(str(file_path))

    file_analysis: FileAnalysis = process_file(abs_file_path=abs_file_path, depth=depth)

    module_scope_info: ScopeInfo
    if scope_filter:
        module_scope_info = file_analysis.scopes[ScopeName(scope_filter)]
    else:
        module_scope_info = file_analysis.scopes[ScopeName("<module>")]

    assignments: List[AssignmentData] = process_scope(module_scope_info)

    graph, unresolved_imports = crawl(
        abs_file_path=abs_file_path,
    )

    json_graph = graph.to_json()

    return {
        "file_analysis": file_analysis,
        "assignments": assignments,
        "scope_filter": scope_filter,
        "graph": json_graph,
        "unresolved_imports": unresolved_imports,
    }
