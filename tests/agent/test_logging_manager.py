"""Tests for agent.logging_manager."""

import logging
from src.agent.logging_manager import setup_logging


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_returns_logger(self):
        """setup_logging returns a Logger instance."""
        logger = setup_logging()
        assert isinstance(logger, logging.Logger)
        assert logger.name == "agentic-testing"

    def test_logger_is_gettable(self):
        """Can retrieve the agentic-testing logger by name."""
        logger = setup_logging()
        same_logger = logging.getLogger("agentic-testing")
        assert same_logger.name == logger.name

    def test_logger_emits_info(self):
        """Logger can emit INFO level messages without error."""
        setup_logging()
        logger = logging.getLogger("agentic-testing")
        # Should not raise
        logger.info("Test message from setup_logging")

    def test_logger_emits_warning(self):
        """Logger can emit WARNING level messages without error."""
        setup_logging()
        logger = logging.getLogger("agentic-testing")
        logger.warning("Test warning message")

    def test_idempotent(self):
        """Calling setup_logging multiple times returns same logger."""
        logger1 = setup_logging()
        logger2 = setup_logging()
        assert logger1.name == logger2.name
        assert logger1.name == "agentic-testing"
