"""Logger Level Enum Module.

This module defines an enumeration of standard logging levels.

Classes:
    Level: An IntEnum representing standard logging severity levels.
"""

import logging
from enum import IntEnum


class Level(IntEnum):
    """Represents standard logging severity levels as integers.

    Each level corresponds to the logging module's built-in constants.
    """

    NOTSET = logging.NOTSET
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
