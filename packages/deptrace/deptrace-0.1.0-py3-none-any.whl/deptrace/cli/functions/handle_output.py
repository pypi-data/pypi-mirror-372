import json
from typing import Dict, Any
from deptrace.formatters.write_graph_output import write_output
from deptrace.logging import get_logger

logger = get_logger(__name__)


def handle_output(
    analysis_result: Dict[str, Any], output_file: str | None, output_format: str | None
) -> None:
    """Handle output of analysis results.

    Args:
        analysis_result: The analysis results to output
        output_file: Optional path to write results to file
        output_format: Format for output file
    """
    if output_file and output_format:
        write_output(analysis_result, output_file, output_format, logger)
    else:
        print(json.dumps(analysis_result, indent=4))
