import os
import sys
from datetime import datetime
from typing import Optional

# ANSI color codes for colored output
COLORS = {
    "reset": "\033[0m",
    "info": "\033[94m",      # blue
    "success": "\033[92m",   # green
    "warning": "\033[93m",   # yellow
    "error": "\033[91m",     # red
    "debug": "\033[95m",     # magenta
    "timestamp": "\033[90m", # gray
    "level": "\033[1m",      # bold
}

# Level names mapping
LEVEL_NAMES = {
    "info": "INFO",
    "success": "SUCCESS",
    "warning": "WARNING",
    "error": "ERROR",
    "debug": "DEBUG",
}

class Logger:
    def __init__(self, log_file: Optional[str] = None, use_colors: bool = True):
        """
        Initialize the logger.
        
        Args:
            log_file (str, optional): Path to the log file. If None, no file logging.
            use_colors (bool): Whether to use colors in console output.
        """
        self.log_file = log_file
        self.use_colors = use_colors and sys.stdout.isatty()
        
        # Create logs directory if file logging is enabled
        if self.log_file:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
    
    def _log(self, level: str, message: str):
        """Internal method to handle logging."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level_name = LEVEL_NAMES.get(level, level.upper())
        
        # Format the log message
        log_message = f"[{timestamp}] [{level_name}] {message}"
        
        # Format for console output with colors
        if self.use_colors:
            console_message = (
                f"{COLORS['timestamp']}[{timestamp}]{COLORS['reset']} "
                f"{COLORS['level']}[{COLORS[level]}{level_name}{COLORS['reset']}{COLORS['level']}]{COLORS['reset']} "
                f"{message}"
            )
        else:
            console_message = log_message
        
        # Print to console
        print(console_message)
        
        # Write to file if enabled
        if self.log_file:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_message + "\n")
    
    def info(self, message: str):
        """Log an info message."""
        self._log("info", message)
    
    def success(self, message: str):
        """Log a success message."""
        self._log("success", message)
    
    def warning(self, message: str):
        """Log a warning message."""
        self._log("warning", message)
    
    def error(self, message: str):
        """Log an error message."""
        self._log("error", message)
    
    def debug(self, message: str):
        """Log a debug message."""
        self._log("debug", message)