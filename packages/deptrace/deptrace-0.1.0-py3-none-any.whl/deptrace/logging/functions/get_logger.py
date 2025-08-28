import logging


def get_logger(name: str | None = None) -> logging.Logger:
    """Get a logger instance with the specified name.

    Args:
        name: The name for the logger, typically __name__

    Returns:
        A configured logger instance
    """
    if name is None:
        name = "deptrace"

    return logging.getLogger(name)
