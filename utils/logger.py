import logging
from typing import Optional


def get_logger(
    name: str = "AgenticDrone",
    level: int = logging.INFO
) -> logging.Logger:
    """
    Creates and returns a configured logger instance.

    Args:
        name: Name of the logger (used as log source).
        level: Logging level (INFO by default).

    Returns:
        logging.Logger: Configured logger instance.
    """

    logger = logging.getLogger(name)

    # Prevent duplicate handlers in interactive environments
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Log format optimized for agentic systems
    formatter = logging.Formatter(
        "[%(levelname)s] [%(name)s] %(message)s"
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.propagate = False

    return logger
