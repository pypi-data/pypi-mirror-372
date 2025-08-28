"""
Logger utilities for AutoDS Copilot.

This module provides centralized logging configuration and utilities
for the entire AutoDS Copilot package.
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Union


def get_logger(name: str, level: Optional[Union[str, int]] = None) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (typically __name__ from calling module)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Don't add handlers multiple times
    if logger.handlers:
        return logger
    
    # Set level
    if level is None:
        level = logging.INFO
    elif isinstance(level, str):
        level = getattr(logging, level.upper())
    
    logger.setLevel(level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Prevent propagation to avoid duplicate messages
    logger.propagate = False
    
    return logger


def configure_logging(level: Union[str, int] = logging.INFO, 
                     log_file: Optional[Path] = None) -> None:
    """
    Configure global logging settings for the package.
    
    Args:
        level: Global logging level
        log_file: Optional file path for log output
    """
    # Convert string level to int if needed
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    
    # Basic configuration
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add file handler if specified
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Add to root logger
        logging.getLogger().addHandler(file_handler)


class LoggerMixin:
    """
    Mixin class to add logging capabilities to any class.
    
    Usage:
        class MyClass(LoggerMixin):
            def __init__(self):
                super().__init__()
                self.logger.info("MyClass initialized")
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = get_logger(self.__class__.__module__ + '.' + self.__class__.__name__)


def silence_warnings():
    """Silence common warnings from data science libraries."""
    import warnings
    
    # Pandas warnings
    warnings.filterwarnings('ignore', category=FutureWarning)
    warnings.filterwarnings('ignore', category=UserWarning)
    
    # Matplotlib warnings
    warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
    
    # Sklearn warnings
    warnings.filterwarnings('ignore', category=FutureWarning, module='sklearn')
    warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')
    
    # Seaborn warnings
    warnings.filterwarnings('ignore', category=FutureWarning, module='seaborn')


def enable_debug_logging():
    """Enable debug logging for the entire package."""
    configure_logging(level=logging.DEBUG)


def disable_logging():
    """Disable all logging output."""
    logging.disable(logging.CRITICAL)
