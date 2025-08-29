"""Logging utilities for the Jira CLI application."""

import logging
import sys
from typing import Optional


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """Get a logger instance with consistent formatting."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:  # Only add handler if none exists
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    # Set level if provided
    if level is not None:
        logger.setLevel(level)
    elif not logger.level:  # Set default level if none set
        logger.setLevel(logging.WARNING)
    
    return logger
