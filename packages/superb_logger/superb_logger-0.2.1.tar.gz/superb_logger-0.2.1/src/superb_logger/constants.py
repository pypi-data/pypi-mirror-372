"""Constants Module for Superb Logger.

This module defines global constants used throughout the logging system.

Constants:
    ROOT_LOGGER_NAME: Default name of the root logger.
    DEFAULT_FORMAT: Standard log message format string.
    DEFAULT_DATE_FORMAT: Standard date/time format for logs.
"""

ROOT_LOGGER_NAME: str = "root"
DEFAULT_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
