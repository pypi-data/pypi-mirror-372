"""
Logging utilities for driver components.

Provides convenient logging methods and utilities.
"""

import logging
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from unrealon_driver.managers.logger import LoggerManager

logger = logging.getLogger(__name__)


class LoggingUtility:
    """Utility class for driver logging operations."""
    
    def __init__(self, driver_id: str):
        """Initialize logging utility."""
        self.driver_id = driver_id
        self.logger_manager: Optional['LoggerManager'] = None
    
    def log(self, level: str, message: str, context: Optional[Dict[str, Any]] = None):
        """Log message through logger manager."""
        if self.logger_manager:
            self.logger_manager.log(level, message, context)
        else:
            # Fallback to standard logging
            log_func = getattr(logger, level.lower(), logger.info)
            log_func(f"{message} | Context: {context}" if context else message)
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log debug message."""
        self.log("DEBUG", message, context)
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log info message."""
        self.log("INFO", message, context)
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log warning message."""
        self.log("WARNING", message, context)
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log error message."""
        self.log("ERROR", message, context)
    
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log critical message."""
        self.log("CRITICAL", message, context)
