"""
Atikin Logger - A lightweight and beginner-friendly Python logging library.
"""

from .logger import Logger

# Create a default logger instance
log = Logger()

# Expose the main functions
info = log.info
success = log.success
warning = log.warning
error = log.error
debug = log.debug

__version__ = "0.1.0"
__author__ = "Your Name"
__license__ = "MIT"

__all__ = ['Logger', 'log', 'info', 'success', 'warning', 'error', 'debug']