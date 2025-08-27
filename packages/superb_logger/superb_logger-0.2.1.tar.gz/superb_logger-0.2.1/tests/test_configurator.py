"""
Tests for the Configurator module in the Superb Logger package.

This module contains unit tests to verify the functionality of the Configurator class.
"""

import logging
import tempfile
from unittest import mock
from unittest.mock import patch

import pytest

from src.superb_logger.configurator import Configurator, Level
from src.superb_logger.constants import DEFAULT_DATE_FORMAT, DEFAULT_FORMAT


class TestConfigurator:
    """Test suite for the Configurator class."""

    def setup_method(self):
        """Initialize a default Configurator instance before each test."""
        self.config = Configurator(base_level=Level.INFO)

    def test_init(self):
        """Test that the Configurator is initialized with correct attributes."""
        assert self.config.base_level == Level.INFO
        assert isinstance(self.config.loggers, dict)
        assert not self.config.loggers

    @pytest.mark.parametrize("base_level", [Level.DEBUG, Level.WARNING, Level.ERROR])
    def test_init_with_custom_base_level(self, base_level):
        """Test initialization with different base logging levels."""
        config = Configurator(base_level=base_level)
        assert config.base_level == base_level

    @pytest.mark.parametrize(
        "name, level, expected_level",
        [
            ("logger1", None, Level.INFO),
            ("logger2", Level.DEBUG, Level.DEBUG),
            ("logger3", Level.WARNING, Level.WARNING),
            ("logger4", Level.ERROR, Level.ERROR),
            ("logger1", Level.INFO, Level.INFO),
        ],
    )
    def test_get_logger_creates_new_logger(self, name, level, expected_level):
        """Test that get_logger creates a new logger with the correct level."""
        logger = self.config.get_logger(name=name, level=level)
        assert logger.name == name
        assert logger.level == expected_level
        assert name in self.config.loggers

    def test_get_logger_returns_existing_logger(self):
        """Test that get_logger returns an existing logger."""
        logger_name = "existing_logger"
        self.config.get_logger(name=logger_name)
        logger = self.config.get_logger(name=logger_name)
        assert logger is self.config.loggers[logger_name]

    def test_get_logger_sets_custom_level(self):
        """Test that get_logger allows setting a custom level."""
        custom_level = 123

        logger = self.config.get_logger(name="custom_level_logger", level=custom_level)
        assert logger.level == custom_level

    def test_get_logger_adds_console_handler(self):
        """Test that get_logger adds a console handler when requested."""
        logger = self.config.get_logger(name="console_logger", to_console=True)
        assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)

    def test_get_logger_adds_file_handler(self):
        """Test that get_logger adds a file handler when requested."""
        with tempfile.NamedTemporaryFile() as tmpfile:
            logger = self.config.get_logger(
                name="console_logger",
                to_console=True,
                filepath=tmpfile.name,
            )
            assert len(logger.handlers) == 2

    def test_set_loggers_configures_multiple_loggers(self):
        """Test that set_loggers configures multiple loggers at once."""
        logger_names = ["logger1", "logger2"]
        self.config.set_loggers(names=logger_names, level=Level.DEBUG)
        for name in logger_names:
            logger = self.config.loggers[name]
            assert logger.level == Level.DEBUG
            assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)

    def test_get_root_logger(self):
        """Test that get_root_logger retrieves the root logger."""
        root_logger = self.config.get_root_logger()
        assert root_logger.name == "root"

    def test_default_formatter(self):
        """Test that _default_formatter returns a properly configured formatter."""
        formatter = self.config._default_formatter()
        assert formatter._fmt == DEFAULT_FORMAT
        assert formatter.datefmt == DEFAULT_DATE_FORMAT

    def test_set_file_handler(self):
        """Test that _set_file_handler removes duplicate handlers before adding."""
        with tempfile.NamedTemporaryFile() as new_tmpfile:
            with tempfile.NamedTemporaryFile() as tmpfile:
                logger = logging.getLogger("duplicate_test_file_logger")
                handler1 = logging.FileHandler(tmpfile.name)
                logger.addHandler(handler1)
                logger = self.config._set_file_handler(
                    logger,
                    filename=new_tmpfile.name,
                )
                assert len(logger.handlers) == 1

    def test_set_console_handler(self):
        """Test that _set_console_handler removes duplicate handlers before adding."""
        logger = logging.getLogger("duplicate_test_console_logger")
        handler1 = logging.StreamHandler()
        logger.addHandler(handler1)
        logger = self.config._set_console_handler(logger)
        assert len(logger.handlers) == 1

    @patch("logging.Handler.setFormatter")
    def test_set_console_handler_uses_formatter(self, mock_set_formatter: mock.Mock):
        """Test that _set_console_handler uses self.console_formatter."""
        console_formatter = logging.Formatter()
        file_formatter = logging.Formatter()

        config = Configurator(
            console_formatter=console_formatter, file_formatter=file_formatter,
        )

        logger = logging.getLogger("test_logger")
        logger.setLevel(logging.INFO)

        updated_logger = config._set_console_handler(logger)

        assert len(updated_logger.handlers) == 1
        handler = updated_logger.handlers[0]
        assert isinstance(handler, logging.StreamHandler)

        used_formatter = mock_set_formatter.mock_calls[0].kwargs["fmt"]
        assert id(used_formatter) == id(console_formatter)

    @patch("logging.Handler.setFormatter")
    def test_set_file_handler_uses_formatter(self, mock_set_formatter: mock.Mock):
        """Test that _set_console_handler uses self.file_formatter."""
        file_formatter = logging.Formatter()
        config = Configurator(file_formatter=file_formatter)

        logger = logging.getLogger("test_logger")
        logger.setLevel(logging.INFO)

        with tempfile.NamedTemporaryFile() as tmpfile:
            updated_logger = config._set_file_handler(logger, filename=tmpfile.name)

            assert len(updated_logger.handlers) == 2
            handler = updated_logger.handlers[1]
            assert isinstance(handler, logging.FileHandler)

            used_formatter = mock_set_formatter.mock_calls[0].kwargs["fmt"]
            assert id(used_formatter) == id(file_formatter)
