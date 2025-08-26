"""
Logging configuration for the Moku library.

This module sets up logging for the Moku library following best practices
for Python libraries:
- Uses NullHandler by default to avoid unwanted log output
- Allows library users to configure their own logging
- Provides convenience functions for common logging scenarios
"""

import logging
import sys
from typing import Optional

# Create a logger for the moku package
logger = logging.getLogger('moku')

# Add NullHandler to prevent any output by default
# This follows best practice for libraries - let the application control logging
logger.addHandler(logging.NullHandler())

# Set propagation to True so parent loggers can handle our logs
logger.propagate = True


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module within the moku package.
    
    Args:
        name: Module name (e.g., 'session', 'instruments.oscilloscope')
    
    Returns:
        Logger instance for the specified module
    """
    return logging.getLogger(f'moku.{name}')


def enable_debug_logging(level: int = logging.DEBUG, 
                         format_string: Optional[str] = None,
                         stream=None) -> None:
    """
    Enable debug logging for the Moku library.
    
    This is a convenience function for library users to quickly enable
    debug output. Should only be called by the application, not the library.
    
    Args:
        level: Logging level (default: DEBUG)
        format_string: Custom format string (default: includes timestamp, level, module, message)
        stream: Output stream (default: stderr)
    
    Example:
        >>> import moku.logging
        >>> moku.logging.enable_debug_logging()
        >>> # Now all moku operations will log debug information
    """
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    if stream is None:
        stream = sys.stderr
    
    # Remove any existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.StreamHandler):
            logger.removeHandler(handler)
    
    # Create and configure handler
    handler = logging.StreamHandler(stream)
    handler.setLevel(level)
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)
    
    # Add handler and set level
    logger.addHandler(handler)
    logger.setLevel(level)


def disable_debug_logging() -> None:
    """
    Disable debug logging for the Moku library.
    
    Removes stream handlers and resets to NullHandler only.
    """
    # Remove all stream handlers
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.StreamHandler):
            logger.removeHandler(handler)
    
    # Ensure we have at least a NullHandler
    if not logger.handlers:
        logger.addHandler(logging.NullHandler())
    
    # Reset level to default
    logger.setLevel(logging.WARNING)


class LoggingContext:
    """
    Context manager for temporarily enabling debug logging.
    
    Example:
        >>> with moku.logging.LoggingContext():
        ...     # Debug logging enabled here
        ...     moku_device.get_data()
        >>> # Debug logging disabled after context
    """
    
    def __init__(self, level: int = logging.DEBUG, 
                 format_string: Optional[str] = None,
                 stream=None):
        self.level = level
        self.format_string = format_string
        self.stream = stream
        self.previous_level = None
        self.previous_handlers = None
    
    def __enter__(self):
        self.previous_level = logger.level
        self.previous_handlers = logger.handlers[:]
        enable_debug_logging(self.level, self.format_string, self.stream)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore previous state
        logger.handlers = self.previous_handlers
        logger.setLevel(self.previous_level)
        return False