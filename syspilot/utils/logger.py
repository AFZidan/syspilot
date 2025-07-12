"""
Logging utilities
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path


def setup_logging(level=logging.INFO, log_file=None):
    """
    Setup logging configuration

    Args:
        level: Logging level (default: INFO)
        log_file: Path to log file (optional)
    """
    # Create logs directory if it doesn't exist
    log_dir = Path.home() / ".config" / "syspilot" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    if log_file is None:
        log_file = log_dir / f"syspilot_{datetime.now().strftime('%Y%m%d')}.log"

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Log startup message
    logging.info(f"SysPilot logging initialized - Level: {logging.getLevelName(level)}")
    logging.info(f"Log file: {log_file}")


def get_logger(name):
    """
    Get logger instance

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
