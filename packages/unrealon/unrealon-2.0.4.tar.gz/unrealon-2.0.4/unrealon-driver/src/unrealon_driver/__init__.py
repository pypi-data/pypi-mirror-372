"""
UnrealOn Driver SDK - Refactored

Clean, simple, powerful API for parser development.
Simplified architecture with all original functionality.

Key Features:
- UniversalDriver - Simple unified API
- All managers integrated cleanly
- WebSocket communication with RPC
- Module system for extensibility
- Clean decorator system
- No complex inheritance chains
"""

# Version info
from unrealon_core.version import get_driver_version

# Core API - Simple and clean
from .driver import (
    UniversalDriver,
    DriverConfig,
    DriverMode
)

from .driver.communication import (
    DriverSession,
    WebSocketClient
)

# Managers - Clean resource management
from .managers import (
    LoggerManager,
    HttpManager,
    BrowserManager,
    CacheManager,
    ProxyManager,
    ThreadManager,
    UpdateManager,
    ManagerRegistry
)

# Module system - Extensible architecture
from .core_module import (
    BaseModule,
    DriverModule,
    ModuleConfig,
    EventManager,
    ModuleRegistry,
    ModuleStatus,
    EventType,
    HealthStatus
)

# Decorators - Clean task management
from .decorators import (
    task,
    retry,
    schedule,
    timing
)

__version__ = get_driver_version()
__author__ = "UnrealOn Team"
__phase__ = "Phase 3.8: Clean Refactor"

__all__ = [
    # Version
    "__version__",
    "__author__", 
    "__phase__",
    
    # Core API
    "UniversalDriver",
    "DriverConfig",
    "DriverMode", 
    "DriverSession",
    "WebSocketClient",
    
    # Managers
    "LoggerManager",
    "HttpManager",
    "BrowserManager", 
    "CacheManager",
    "ProxyManager",
    "ThreadManager",
    "UpdateManager",
    "ManagerRegistry",
    
    # Module system
    "BaseModule",
    "DriverModule",
    "ModuleConfig",
    "EventManager",
    "ModuleRegistry",
    "ModuleStatus",
    "EventType",
    "HealthStatus",
    
    # Decorators
    "task",
    "retry",
    "schedule", 
    "timing",
]
