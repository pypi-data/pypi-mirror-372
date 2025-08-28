import argparse
from typing import Tuple, Optional

from deptrace.cli.actions import AnalysisAction


def parse_args() -> Tuple[
    str,
    int,
    str,
    Optional[str],
    Optional[str],
    Optional[str],
    AnalysisAction,
    Optional[str],
]:
    """Parse command line arguments.

    Returns:
        Tuple containing:
        - entry_file: Path to the Python file to analyze
        - depth: Depth to analyze
        - log_level: Logging level to use
        - scope_filter: Optional scope name to filter the output
        - output_file: Optional path to write analysis results
        - output_format: Format for output file (defaults to 'json')
        - action: Type of analysis to perform (AnalysisAction enum)
        - target_function: Target function name for call tree analysis
    """
    arg_description = "Analyze dependencies in Python code"
    parser = argparse.ArgumentParser(description=arg_description)

    parser.add_argument(
        "entry_file",
        help="Relative or absolute path to the Python file to analyze",
        type=str,
    )

    parser.add_argument(
        "--depth",
        type=int,
        default=4,
        help="Depth of the analysis",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO"],
        default="INFO",
        help="Set the logging level",
    )

    parser.add_argument(
        "--scope-filter",
        type=str,
        help="Filter output to a specific scope (e.g. '<module>.outer.Inner.method')",
    )

    parser.add_argument(
        "-o",
        "--output-file",
        help="Write analysis results to specified file",
    )

    parser.add_argument(
        "--output-format",
        choices=["json"],
        default="json",
        help="Format for output file (default: json)",
    )

    parser.add_argument(
        "--action",
        choices=[action.value for action in AnalysisAction],
        default=AnalysisAction.DEPENDENCIES.value,
        help="Type of analysis to perform (default: dependencies)",
    )

    parser.add_argument(
        "--target-function",
        type=str,
        help="Target function name for call tree analysis (required with --action call-tree)",
    )

    args = parser.parse_args()

    # Validate call tree arguments
    if args.action == AnalysisAction.CALL_TREE.value and not args.target_function:
        parser.error("--target-function is required when using --action call-tree")

    return (
        args.entry_file,
        args.depth,
        args.log_level,
        args.scope_filter,
        args.output_file,
        args.output_format,
        AnalysisAction(args.action),
        args.target_function,
    )
