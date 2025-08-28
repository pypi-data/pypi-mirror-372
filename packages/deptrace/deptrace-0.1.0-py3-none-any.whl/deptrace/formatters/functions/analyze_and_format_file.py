from pathlib import Path
from typing import Dict, Any
from deptrace.processors import analyze_file as processor_analyze_file
from deptrace.processors import format_analysis


def analyze_and_format_file(
    file_path: str | Path, depth: int = 4, scope_filter: str | None = None
) -> Dict[str, Any]:
    """Analyze a Python file and return formatted analysis results.

    This function combines the raw analysis from processors with formatting
    to provide the complete formatted output for CLI consumption.

    Args:
        file_path: Path to the Python file to analyze
        depth: Depth of the analysis
        scope_filter: Optional scope name to filter the output

    Returns:
        Dictionary containing formatted analysis results with keys:
        - scopes: formatted scope information
        - assignments: formatted assignment data
        - graph: dependency graph
        - unresolved_imports: unresolved imports
    """
    # Get raw analysis results from processors
    raw_results = processor_analyze_file(
        file_path=file_path, depth=depth, scope_filter=scope_filter
    )

    # Format the core analysis results using processors formatting
    formatted_output = format_analysis(
        analysis=raw_results["file_analysis"],
        scope_filter=raw_results["scope_filter"],
        assignments=raw_results["assignments"],
    )

    # Add graph and unresolved imports to formatted output
    formatted_output["graph"] = raw_results["graph"]
    formatted_output["unresolved_imports"] = raw_results["unresolved_imports"]

    return formatted_output
