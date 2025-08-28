import logging
from typing import Optional


def configure_logging(level: Optional[int] = None) -> None:
    """Configure the root logger for the application.

    Sets up the root logger with appropriate handlers and formatting.
    This should be called once at application startup.

    Args:
        level: The logging level (defaults to INFO)
    """
    if level is None:
        level = logging.INFO

    # Get the root logger
    root_logger = logging.getLogger()

    # Clear any existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Set the root logger level
    root_logger.setLevel(level)

    # Create handler to stderr (standard practice)
    handler = logging.StreamHandler()

    # Set up formatter
    formatter = logging.Formatter("%(asctime)s [%(name)s] [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)

    # Add the handler to the root logger
    root_logger.addHandler(handler)
