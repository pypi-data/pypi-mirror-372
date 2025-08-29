"""
Clean module system for UnrealOn Driver.
"""

from .protocols import (
    BaseModule,
    ModuleStatus,
    EventType,
    HealthStatus,
    ModuleEvent,
    HealthCheckResult
)
from .config import ModuleConfig
from .base import DriverModule
from .event_manager import EventManager
from .registry import ModuleRegistry

__all__ = [
    # Protocols and enums
    "BaseModule",
    "ModuleStatus",
    "EventType", 
    "HealthStatus",
    "ModuleEvent",
    "HealthCheckResult",
    
    # Base classes
    "ModuleConfig",
    "DriverModule",
    
    # System components
    "EventManager",
    "ModuleRegistry",
]
