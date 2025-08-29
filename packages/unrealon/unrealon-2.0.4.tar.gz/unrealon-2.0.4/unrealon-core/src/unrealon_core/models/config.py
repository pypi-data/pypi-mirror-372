"""
Config models - Phase 2 update.

Import from strictly typed websocket models to avoid duplication.
Following critical requirements - no raw Dict[str, Any].
"""

# Import strictly typed models from websocket package
from .websocket.config import (
    DriverConfiguration,
    LoggingConfiguration,
    TaskConfiguration,
    ProxyConfiguration
)
from .base import ConfigBaseModel

# System config that doesn't exist in websocket models yet
class SystemConfig(ConfigBaseModel):
    """System-wide configuration."""
    
    redis_url: str = "redis://localhost:6379/0"
    websocket_url: str = "ws://localhost:8000/ws"
    max_workers: int = 10
    debug: bool = False

# Legacy compatibility - map to new typed models
HttpConfig = TaskConfiguration  # HTTP settings are part of task config
ProxyConfig = ProxyConfiguration
LoggingConfig = LoggingConfiguration
BrowserConfig = TaskConfiguration  # Browser settings are part of task config
CacheConfig = SystemConfig  # Cache settings are system-wide
ThreadConfig = TaskConfiguration  # Thread settings are part of task config

__all__ = [
    'DriverConfiguration',
    'LoggingConfiguration', 
    'TaskConfiguration',
    'ProxyConfiguration',
    'SystemConfig',
    # Legacy names
    'HttpConfig',
    'ProxyConfig',
    'LoggingConfig',
    'BrowserConfig',
    'CacheConfig',
    'ThreadConfig'
]