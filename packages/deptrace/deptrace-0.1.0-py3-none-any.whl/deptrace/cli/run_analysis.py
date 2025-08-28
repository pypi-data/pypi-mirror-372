import logging
from pathlib import Path

from deptrace.cli.actions import AnalysisAction
from deptrace.cli.parse_args import parse_args
from deptrace.logging import configure_logging, get_logger
from deptrace.cli.functions.analyze_file import analyze_file
from deptrace.cli.functions.handle_output import handle_output

logger = get_logger(__name__)


def run_analysis() -> None:
    (
        file_path,
        depth,
        parsed_log_level,
        scope_filter,
        output_file,
        output_format,
        action,
        target_function,
    ) = parse_args()

    log_level = getattr(logging, parsed_log_level)
    configure_logging(level=log_level)
    logger.debug("Starting analysis with parameters:")
    logger.debug(f"  file_path: {file_path}")
    logger.debug(f"  depth: {depth}")
    logger.debug(f"  log_level: {log_level}")

    if scope_filter:
        logger.debug(f"  scope_filter: {scope_filter}")

    if output_file:
        logger.debug(f"  output_file: {output_file}")
        logger.debug(f"  output_format: {output_format}")

    if action == AnalysisAction.CALL_TREE:
        from deptrace.visitors.call_tree import analyze_project_call_tree

        logger.info(f"Analyzing tree for func '{target_function}' in '{file_path}'")

        # For call tree, we need to analyze the directory containing the file
        file_path_obj = Path(file_path)
        if file_path_obj.is_file():
            # Analyze the directory containing the file
            project_dir = file_path_obj.parent
        else:
            # Assume it's already a directory
            project_dir = file_path_obj

        analysis_result = analyze_project_call_tree(str(project_dir), target_function)

    else:
        logger.info(f"Analyzing dependencies for file '{file_path}'")

        analysis_result = analyze_file(
            file_path=file_path,
            depth=depth,
            scope_filter=scope_filter,
        )

    logger.info("Analysis complete!")

    handle_output(
        analysis_result=analysis_result,
        output_file=output_file,
        output_format=output_format,
    )
