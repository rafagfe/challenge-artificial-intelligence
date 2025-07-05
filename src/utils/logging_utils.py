"""
Logging utility functions for structured logging.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None,
) -> logging.Logger:
    """
    Setup structured logging for the application.

    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (Optional[str]): Path to log file (optional)
        format_string (Optional[str]): Custom format string (optional)

    Returns:
        logging.Logger: Configured logger instance
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Create formatter
    formatter = logging.Formatter(format_string)

    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name (str): Logger name (usually __name__)

    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)


def log_function_call(func_name: str, args: tuple, kwargs: dict) -> None:
    """
    Log function call details for debugging.

    Args:
        func_name (str): Function name
        args (tuple): Function arguments
        kwargs (dict): Function keyword arguments
    """
    logger = get_logger(__name__)
    logger.debug(f"Calling {func_name} with args={args}, kwargs={kwargs}")


def log_error(error: Exception, context: str = "") -> None:
    """
    Log error with context information.

    Args:
        error (Exception): Exception instance
        context (str): Additional context information
    """
    logger = get_logger(__name__)
    if context:
        logger.error(f"Error in {context}: {type(error).__name__}: {error}")
    else:
        logger.error(f"Error: {type(error).__name__}: {error}")


def log_performance(operation: str, duration: float) -> None:
    """
    Log performance metrics.

    Args:
        operation (str): Operation name
        duration (float): Duration in seconds
    """
    logger = get_logger(__name__)
    logger.info(f"Performance: {operation} completed in {duration:.2f}s")
