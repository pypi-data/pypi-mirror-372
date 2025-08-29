"""
UnrealOn Core Models

All Pydantic models used across the UnrealOn system.
These models provide strict validation and serialization for:
- WebSocket communication
- RPC calls
- Database operations
- Configuration management

Phase 1: Foundation models with 100% validation coverage
"""

from .base import (
    UnrealOnBaseModel, 
    TimestampedModel, 
    IdentifiedModel, 
    StatusModel,
    MetadataModel,
    FullBaseModel,
    SimpleBaseModel
)

from .communication import (
    WebSocketMessage
)

from .driver import (
    DriverInfo,
    DriverConfig, 
    DriverCapability
)

from .task import (
    TaskAssignmentData,
    TaskResultData, 
    TaskParameters,
    TaskMetadata
)

# Proxy models moved to websocket.proxy

from .logging import (
    LogEntry,
    LogQuery,
    LogMetrics
)

from .config import (
    SystemConfig,
    HttpConfig,
    ProxyConfig,
    BrowserConfig, 
    LoggingConfig,
    CacheConfig,
    ThreadConfig
)

__all__ = [
    # Base models
    "UnrealOnBaseModel",
    "TimestampedModel", 
    "IdentifiedModel",
    "StatusModel",
    "MetadataModel",
    "FullBaseModel",
    "SimpleBaseModel",
    
    # Communication models
    "WebSocketMessage",
    
    # Driver models
    "DriverInfo",
    "DriverConfig", 
    "DriverCapability",
    
    # Task models
    "TaskAssignmentData",
    "TaskResultData", 
    "TaskParameters",
    "TaskMetadata",
    
    # Proxy models moved to websocket.proxy
    
    # Logging models
    "LogEntry",
    "LogQuery",
    "LogMetrics",
    
    # Configuration models
    "SystemConfig",
    "HttpConfig",
    "ProxyConfig",
    "BrowserConfig", 
    "LoggingConfig",
    "CacheConfig",
    "ThreadConfig",
]
