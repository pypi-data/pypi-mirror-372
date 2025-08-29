"""
UnrealOn Core Exceptions

Custom exception hierarchy for the UnrealOn system.
Provides specific exceptions for different error conditions
with proper error codes and context information.

Phase 1: Foundation exceptions with proper hierarchy
"""

from .base import UnrealOnError, UnrealOnWarning
from .validation import ValidationError, ConfigurationError
from .communication import CommunicationError, WebSocketError, RPCError
from .driver import DriverError, DriverNotFoundError, DriverTimeoutError
from .task import TaskError, TaskTimeoutError, TaskValidationError
from .proxy import ProxyError, ProxyNotAvailableError, ProxyTimeoutError

__all__ = [
    # Base exceptions
    "UnrealOnError",
    "UnrealOnWarning",
    
    # Validation exceptions
    "ValidationError",
    "ConfigurationError",
    
    # Communication exceptions
    "CommunicationError",
    "WebSocketError", 
    "RPCError",
    
    # Driver exceptions
    "DriverError",
    "DriverNotFoundError",
    "DriverTimeoutError",
    
    # Task exceptions
    "TaskError",
    "TaskTimeoutError",
    "TaskValidationError",
    
    # Proxy exceptions
    "ProxyError",
    "ProxyNotAvailableError",
    "ProxyTimeoutError",
]
