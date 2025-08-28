"""Logger configuration module for fnb.

This module provides centralized logging setup using loguru,
replacing print statements with structured logging.
"""

import os
import sys
from pathlib import Path
from typing import Optional

from loguru import logger
from platformdirs import user_log_dir


class LoggerManager:
    """Manages logging configuration for fnb application."""

    def __init__(self) -> None:
        """Initialize the logger manager."""
        self._is_configured = False
        self._log_dir = Path(user_log_dir("fnb", "qumasan"))
        self._log_file = self._log_dir / "fnb.log"

    def configure(
        self,
        level: str = "INFO",
        enable_file_logging: Optional[bool] = None,
        console_format: Optional[str] = None,
        file_format: Optional[str] = None,
    ) -> None:
        """Configure the logger with specified settings.

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR)
            enable_file_logging: Whether to enable file logging (None for auto-detect)
            console_format: Console log format (None for default)
            file_format: File log format (None for default)

        Note:
            File logging auto-detection:
            - Enabled by default in production
            - Can be disabled via FNB_DISABLE_FILE_LOGGING=1 environment variable
            - Disabled automatically in test environments
        """
        if self._is_configured:
            return

        # Auto-detect file logging if not specified
        if enable_file_logging is None:
            enable_file_logging = self._should_enable_file_logging()

        # Remove default handler
        logger.remove()

        # Console handler with format
        console_fmt = console_format or (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )

        logger.add(
            sys.stderr,
            format=console_fmt,
            level=level,
            colorize=True,
            enqueue=True,
        )

        # File handler if enabled
        if enable_file_logging:
            self._log_dir.mkdir(parents=True, exist_ok=True)

            file_fmt = file_format or (
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
                "{level: <8} | "
                "{name}:{function}:{line} - "
                "{message}"
            )

            logger.add(
                self._log_file,
                format=file_fmt,
                level=level,
                rotation="10 MB",
                retention="7 days",
                compression="gz",
                enqueue=True,
            )

            # Inform user about log file location
            logger.info(f"Log file: {self._log_file}")

        self._is_configured = True

    def _should_enable_file_logging(self) -> bool:
        """Determine if file logging should be enabled by default.

        Returns:
            True if file logging should be enabled
        """
        # Disable if explicitly requested
        if os.getenv("FNB_DISABLE_FILE_LOGGING", "").lower() in ("1", "true", "yes"):
            return False

        # Disable in test environments
        if any(
            test_var in os.environ
            for test_var in ["PYTEST_CURRENT_TEST", "_PYTEST_RAISE"]
        ):
            return False

        # Enable by default in production
        return True

    def get_logger(self, name: Optional[str] = None) -> "logger":
        """Get a logger instance.

        Args:
            name: Logger name (None for root logger)

        Returns:
            Logger instance
        """
        if not self._is_configured:
            self.configure()

        if name:
            return logger.bind(name=name)
        return logger

    @property
    def log_file_path(self) -> Path:
        """Get the log file path.

        Returns:
            Path to the log file
        """
        return self._log_file

    @property
    def is_configured(self) -> bool:
        """Check if logger is configured.

        Returns:
            True if logger is configured
        """
        return self._is_configured


# Global logger manager instance
_logger_manager = LoggerManager()


def get_logger(name: Optional[str] = None) -> "logger":
    """Get a logger instance (convenience function).

    Args:
        name: Logger name (None for root logger)

    Returns:
        Logger instance
    """
    return _logger_manager.get_logger(name)


def configure_logger(
    level: str = "INFO",
    enable_file_logging: Optional[bool] = None,
    console_format: Optional[str] = None,
    file_format: Optional[str] = None,
) -> None:
    """Configure the global logger (convenience function).

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        enable_file_logging: Whether to enable file logging (None for auto-detect)
        console_format: Console log format (None for default)
        file_format: File log format (None for default)

    Note:
        See LoggerManager.configure() for auto-detection details.
    """
    _logger_manager.configure(
        level=level,
        enable_file_logging=enable_file_logging,
        console_format=console_format,
        file_format=file_format,
    )


def get_log_file_path() -> Path:
    """Get the log file path (convenience function).

    Returns:
        Path to the log file
    """
    return _logger_manager.log_file_path
