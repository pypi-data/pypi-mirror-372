import os
import json
import logging
from typing import Dict, Any


def write_output(json_data: Dict[str, Any], output_file: str, output_format: str, logger: logging.Logger) -> None:
    """Write analysis results to file in specified format.

    Args:
        graph: The dependency graph to output
        output_file: Path to output file
        output_format: Format to write (currently only 'json' supported)
    """
    if output_format == "json":
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)
            f.write("\n")
        logger.info(f"Output written to {output_file}")
    else:
        logger.error(f"Unsupported output format: {output_format}")
