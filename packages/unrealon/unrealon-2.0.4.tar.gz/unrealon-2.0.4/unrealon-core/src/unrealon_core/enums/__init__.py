"""
UnrealOn Core Enums

All enums and constants used across the UnrealOn system.
These provide type safety and consistent values throughout the codebase.

Phase 1: Foundation enums with strict validation
"""

from .status import DriverStatus, TaskStatus, ProxyStatus, LogLevel
from .types import MessageType, ProxyType, TaskPriority

__all__ = [
    # Status enums
    "DriverStatus",
    "TaskStatus", 
    "ProxyStatus",
    "LogLevel",
    
    # Type enums
    "MessageType",
    "ProxyType",
    "TaskPriority",
]
