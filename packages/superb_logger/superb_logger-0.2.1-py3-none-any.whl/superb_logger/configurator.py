"""Superb Logger Configurator Module.

This module provides a flexible and customizable logging configuration utility.
It allows setting up console and file handlers for multiple loggers with ease.

Classes:
    Configurator: Central class to configure and retrieve logger instances.
"""

from logging import FileHandler, Formatter, Logger, StreamHandler, getLogger

from .constants import DEFAULT_DATE_FORMAT, DEFAULT_FORMAT, ROOT_LOGGER_NAME
from .enums import Level


class Configurator:
    """Main class to configure and manage logger instances.

    Attributes:
        base_level: Default logging level for all loggers.
        console_formatter: Formatter used for console output.
        file_formatter: Formatter used for file output.
        loggers: Dictionary storing already configured logger instances.

    """

    base_level: int
    console_formatter: Formatter
    file_formatter: Formatter
    loggers: dict[str, Logger]

    def __init__(
        self,
        *,
        base_level: Level | int = Level.INFO,
        console_formatter: Formatter | None = None,
        file_formatter: Formatter | None = None,
    ) -> None:
        """Initialize the configurator with a default logging level.

        Args:
            base_level: Base logging level for all loggers (default is INFO).
            console_formatter: Optional formatter for console output.
            file_formatter: Optional formatter for file output.

        Example:
            ```python
            from superb_logger import Configurator, Level
            config = Configurator(base_level=Level.INFO)
            ```

        """
        self.loggers = {}
        self.base_level = base_level
        self.console_formatter = console_formatter or self._default_formatter()
        self.file_formatter = file_formatter or self._default_formatter()

    def get_logger(
        self,
        name: str,
        *,
        level: Level | None = None,
        to_console: bool = True,
        filepath: str | None = None,
    ) -> Logger:
        """Get or create a configured logger instance.

        Args:
            name: Name of the logger.
            level: Logging level for this specific logger.
            to_console: Whether to add a console handler.
            filepath: Path to a file for logging output.

        Returns:
            A configured Logger instance.

        Example:
            ```python
            from superb_logger import Configurator
            config = Configurator()
            logger = config.get_logger(name="app", to_console=True)
            ```

        """
        logger = self.loggers.get(name)
        if logger is None:
            logger = getLogger(name)

        logger.setLevel(level or self.base_level)
        if to_console:
            logger = self._set_console_handler(logger=logger)
        if filepath:
            logger = self._set_file_handler(logger=logger, filename=filepath)

        self.loggers[name] = logger
        return logger

    def get_root_logger(self) -> Logger:
        """Retrieve the root logger configured by this instance.

        Returns:
            The root logger instance.

        Example:
            ```python
            from superb_logger import Configurator
            config = Configurator()
            root_logger = config.get_root_logger()
            ```

        """
        return self.get_logger(name=ROOT_LOGGER_NAME)

    def set_loggers(
        self,
        names: list[str],
        *,
        level: Level | None = None,
        to_console: bool = True,
    ) -> None:
        """Configure multiple loggers at once.

        Args:
            names: List of logger names to configure.
            level: Logging level for all these loggers.
            to_console: Whether to add a console handler.

        Example:
            ```python
            from superb_logger import Configurator
            config = Configurator()
            config.set_loggers(names=["app", "db"], level="DEBUG")
            ```

        """
        for name in names:
            self.get_logger(name=name, level=level, to_console=to_console)

    @staticmethod
    def _default_formatter() -> Formatter:
        """Create and return a default log message formatter.

        Returns:
            A default Formatter instance.

        Example:
            ```python
            from superb_logger.configurator import Configurator
            formatter = Configurator._default_formatter()
            ```

        """
        return Formatter(fmt=DEFAULT_FORMAT, datefmt=DEFAULT_DATE_FORMAT)

    @staticmethod
    def _delete_handlers(
        logger: Logger,
        handler_class: type[FileHandler | StreamHandler],
    ) -> Logger:
        """Remove existing handlers of the specified class from the logger.

        Args:
            logger: The logger to modify.
            handler_class: Class of handlers to remove.

        Returns:
            Updated logger instance.

        Example:
            ```python
            from superb_logger.configurator import Configurator
            logger = Configurator().get_logger("test")
            logger = Configurator._delete_handlers(logger, StreamHandler)
            ```

        """
        for handler in logger.handlers:
            if isinstance(handler, handler_class):
                logger.removeHandler(handler)

        return logger

    def _set_file_handler(self, logger: Logger, filename: str) -> Logger:
        """Add a file handler to the specified logger.

        Args:
            logger: Logger to which the handler will be added.
            filename: Path to the log file.

        Returns:
            Updated logger instance.

        Raises:
            OSError: If the file cannot be opened.

        Example:
            ```python
            from superb_logger.configurator import Configurator
            logger = Configurator().get_logger("file_logger")
            logger = Configurator()._set_file_handler(logger, "app.log")
            ```

        """
        file_handler = FileHandler(filename=filename)
        file_handler.setFormatter(fmt=self.file_formatter)
        logger = self._delete_handlers(logger=logger, handler_class=FileHandler)
        logger.addHandler(hdlr=file_handler)
        return logger

    def _set_console_handler(self, logger: Logger) -> Logger:
        """Add a console handler to the specified logger.

        Args:
            logger: Logger to which the handler will be added.

        Returns:
            Updated logger instance.

        Example:
            ```python
            from superb_logger.configurator import Configurator
            logger = Configurator().get_logger("console_logger")
            logger = Configurator()._set_console_handler(logger)
            ```

        """
        console_handler = StreamHandler()
        console_handler.setFormatter(fmt=self.console_formatter)
        logger = self._delete_handlers(logger=logger, handler_class=StreamHandler)
        logger.addHandler(hdlr=console_handler)
        return logger
