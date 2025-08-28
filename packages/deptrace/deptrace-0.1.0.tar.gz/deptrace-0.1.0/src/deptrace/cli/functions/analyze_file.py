from pathlib import Path
from typing import Dict, Any
from deptrace.formatters import analyze_and_format_file


def analyze_file(
    file_path: str | Path, depth: int = 4, scope_filter: str | None = None
) -> Dict[str, Any]:
    """Analyze a Python file and return structured analysis results.

    Args:
        file_path: Path to the Python file to analyze
        depth: Depth of the analysis
        scope_filter: Optional scope name to filter the output

    Returns:
        Dictionary containing analysis results with keys:
        - scopes: formatted scope information  
        - assignments: formatted assignment data
        - graph: dependency graph
        - unresolved_imports: unresolved imports
    """
    return analyze_and_format_file(
        file_path=file_path, depth=depth, scope_filter=scope_filter
    )
