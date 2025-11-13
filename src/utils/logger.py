"""Logging module with 4-level logging and file rotation.

Provides centralized logging functionality for the application with
DEBUG, INFO, WARNING, and ERROR levels, plus automatic log file rotation.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


class Logger:
    """Application logger with file rotation support."""

    _instance: Optional[logging.Logger] = None
    _log_dir: Path = Path(os.getenv("APPDATA", "")) / "WSLScreenshot" / "logs"

    @classmethod
    def get_logger(cls, name: str = "WSLScreenshot") -> logging.Logger:
        """Get or create the application logger.

        Args:
            name: Logger name (default: "WSLScreenshot")

        Returns:
            Configured logger instance
        """
        if cls._instance is None:
            cls._instance = cls._setup_logger(name)
        return cls._instance

    @classmethod
    def _setup_logger(cls, name: str) -> logging.Logger:
        """Setup logger with file and console handlers.

        Args:
            name: Logger name

        Returns:
            Configured logger
        """
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # Create log directory if it doesn't exist
        cls._log_dir.mkdir(parents=True, exist_ok=True)

        # Create file handler with rotation (10MB max, keep 5 files)
        log_file = cls._log_dir / "app.log"
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10MB
        )
        file_handler.setLevel(logging.DEBUG)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(module)s:%(funcName)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger


# Convenience functions
def get_logger(name: str = "WSLScreenshot") -> logging.Logger:
    """Get the application logger.

    Args:
        name: Logger name (default: "WSLScreenshot")

    Returns:
        Logger instance
    """
    return Logger.get_logger(name)


def log_debug(message: str, **kwargs) -> None:
    """Log debug message."""
    get_logger().debug(message, **kwargs)


def log_info(message: str, **kwargs) -> None:
    """Log info message."""
    get_logger().info(message, **kwargs)


def log_warning(message: str, **kwargs) -> None:
    """Log warning message."""
    get_logger().warning(message, **kwargs)


def log_error(message: str, **kwargs) -> None:
    """Log error message."""
    get_logger().error(message, **kwargs)
