"""
Logging Configuration for Stock Agent System

Provides centralized logging configuration with:
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- File and console handlers
- Structured log formatting with timestamps
- Automatic log rotation
"""

import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logger(
    name: str = 'agent',
    level: int = logging.INFO,
    log_dir: Optional[str] = None,
    console_output: bool = True,
    file_output: bool = True
) -> logging.Logger:
    """
    Set up a logger with both file and console handlers.

    Args:
        name: Logger name (default: 'agent')
        level: Logging level (default: INFO)
        log_dir: Directory for log files (default: ./logs)
        console_output: Enable console output (default: True)
        file_output: Enable file output (default: True)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler with rotation
    if file_output:
        if log_dir is None:
            # Default to ./logs directory
            log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')

        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        # Create log file with date in filename
        log_file = log_path / f'agent_{datetime.now().strftime("%Y%m%d")}.log'

        # Use RotatingFileHandler to prevent huge log files
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=30,  # Keep 30 backup files
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = 'agent') -> logging.Logger:
    """
    Get an existing logger or create a new one with default configuration.

    Args:
        name: Logger name (default: 'agent')

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    # If logger doesn't have handlers, set it up
    if not logger.handlers:
        # Read log level from settings
        try:
            from agent.config import settings
            level_str = settings.logging.level.upper()
            level = getattr(logging, level_str, logging.INFO)
        except (ImportError, AttributeError):
            level = logging.INFO
        
        setup_logger(name, level=level)

    return logger


# Set up default logger on module import
try:
    from agent.config import settings
    level_str = settings.logging.level.upper()
    default_level = getattr(logging, level_str, logging.INFO)
except (ImportError, AttributeError):
    default_level = logging.INFO

default_logger = setup_logger(level=default_level)

# Suppress DEBUG logs from noisy third-party libraries
# These libraries can be very verbose at DEBUG level
logging.getLogger('yfinance').setLevel(logging.WARNING)
logging.getLogger('peewee').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('charset_normalizer').setLevel(logging.WARNING)
