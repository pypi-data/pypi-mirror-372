# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import sys
from functools import partial
from pathlib import Path
from typing import Optional

from . import metadata

# Configure global logging
logging_message_format = "%(asctime)s: %(levelname)s: %(message)s"
logging.basicConfig(format=logging_message_format)
logging.getLogger(metadata.name).setLevel(100)

# Add a custom FATAL logging level (90)
logging.addLevelName(90, "FATAL")
# Override the existing FATAL level with our custom level
# Note: This will cause a mypy error but is needed for backward compatibility
logging.FATAL = 90  # type: ignore[misc]

# Logging level constants that wrap stdlib logging module constants
NOTSET = logging.NOTSET
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL
FATAL = logging.FATAL

# Set the default logging level to 100
logging.getLogger(metadata.name).setLevel(100)


def log(lvl: int, msg: str) -> None:
    """Send the log message with the specified level

    This function will send the log message to the logger with the specified
    logging level.  This function should not be directly invoked.  Use one
    of the partials to send a log message with a given level.

    Args:
        lvl (int): The logging level of the message
        msg (str): The message to write to the logger
    """
    logging.getLogger(metadata.name).log(lvl, msg)


debug = partial(log, logging.DEBUG)
info = partial(log, logging.INFO)
warning = partial(log, logging.WARNING)
error = partial(log, logging.ERROR)
critical = partial(log, logging.CRITICAL)


def exception(exc: Exception) -> None:
    """
    Log an exception error

    Args:
        exc (Exception): Exception to log as an error

    Returns:
        None
    """
    log(logging.ERROR, str(exc))


def fatal(msg: str) -> None:
    """
    Log a fatal error

    A fatal error will log the message using level 90 (FATAL) and print
    an error message to stdout.  It will then exit the application with
    return code 1

    Args:
        msg (str): The message to print

    Returns:
        None

    Raises:
        None
    """
    log(logging.FATAL, msg)
    print(f"ERROR: {msg}")
    sys.exit(1)


def set_level(lvl: int, propagate: bool = False) -> None:
    """Set logging level for all loggers in the current Python process.

    Args:
        lvl (int): Logging level (e.g., logging.INFO, logging.DEBUG).  This
            is a required argument

        propagate (bool): Setting this value to True will also turn on
            logging for httpx and httpcore.

    Returns:
        None

    Raises:
        None
    """
    logging.getLogger(metadata.name).setLevel(lvl)

    if propagate is True:
        logging.getLogger("httpx").setLevel(lvl)
        logging.getLogger("httpcore").setLevel(lvl)

    logging.getLogger(metadata.name).log(
        logging.INFO, f"ipsdk version {metadata.version}"
    )
    logging.getLogger(metadata.name).log(logging.INFO, f"Logging level set to {lvl}")
    logging.getLogger(metadata.name).log(
        logging.INFO, f"Logging propagation is {propagate}"
    )


def add_file_handler(
    file_path: str, level: Optional[int] = None, format_string: Optional[str] = None
) -> None:
    """Add a file handler to the ipsdk logger.

    Args:
        file_path (str): Path to the log file. Parent directories will be created if they don't exist.
        level (Optional[int]): Logging level for the file handler. If None, uses the logger's current level.
        format_string (Optional[str]): Custom format string for the file handler.
                                     If None, uses the default logging_message_format.

    Returns:
        None

    Raises:
        OSError: If the log file cannot be created or accessed.
    """
    logger = logging.getLogger(metadata.name)

    # Create parent directories if they don't exist
    log_file = Path(file_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Create file handler
    file_handler = logging.FileHandler(file_path)

    # Set level - use provided level or current logger level
    if level is not None:
        file_handler.setLevel(level)
    else:
        file_handler.setLevel(logger.level)

    # Set format - use provided format or default
    if format_string is not None:
        formatter = logging.Formatter(format_string)
    else:
        formatter = logging.Formatter(logging_message_format)

    file_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(file_handler)

    logger.log(logging.INFO, f"File logging enabled: {file_path}")


def remove_file_handlers() -> None:
    """Remove all file handlers from the ipsdk logger.

    Returns:
        None
    """
    logger = logging.getLogger(metadata.name)

    # Get all file handlers
    file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]

    # Remove each file handler
    for handler in file_handlers:
        logger.removeHandler(handler)
        handler.close()

    if file_handlers:
        logger.log(logging.INFO, f"Removed {len(file_handlers)} file handler(s)")


def configure_file_logging(
    file_path: str,
    level: int = logging.INFO,
    propagate: bool = False,
    format_string: Optional[str] = None,
) -> None:
    """Configure both console and file logging in one call.

    This is a convenience function that sets the logging level and adds file logging.

    Args:
        file_path (str): Path to the log file. Parent directories will be created
            if they don't exist.
        level (int): Logging level (e.g., logging.INFO, logging.DEBUG).
            Default is INFO.
        propagate (bool): Setting this value to True will also turn on logging
            for httpx and httpcore.
        format_string (Optional[str]): Custom format string for the file handler.
                                     If None, uses the default logging_message_format.

    Returns:
        None

    Raises:
        OSError: If the log file cannot be created or accessed.
    """
    # Set the logging level first
    set_level(level, propagate)

    # Add file handler
    add_file_handler(file_path, level, format_string)
