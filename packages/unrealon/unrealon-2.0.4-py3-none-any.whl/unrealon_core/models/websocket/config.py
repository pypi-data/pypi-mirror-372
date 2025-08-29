"""
Configuration WebSocket Models.

Strictly typed models for configuration updates.
No raw dictionaries - all data structures are Pydantic models.

Phase 2: Core Systems - WebSocket Bridge
"""

from typing import Optional, List
from pydantic import Field, ConfigDict

from ..base import UnrealOnBaseModel
from .base import WebSocketMessage, MessageType


class LoggingConfiguration(UnrealOnBaseModel):
    """Logging configuration - strictly typed."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    level: str = Field(
        default="INFO",
        pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Logging level"
    )
    
    batch_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Log batch size"
    )
    
    send_interval: float = Field(
        default=1.0,
        ge=0.1,
        le=60.0,
        description="Log send interval in seconds"
    )
    
    local_logging: bool = Field(
        default=True,
        description="Enable local logging"
    )


class TaskConfiguration(UnrealOnBaseModel):
    """Task configuration - strictly typed."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    max_concurrent_tasks: int = Field(
        default=1,
        ge=1,
        le=100,
        description="Maximum concurrent tasks"
    )
    
    default_timeout: float = Field(
        default=300.0,
        ge=30.0,
        le=3600.0,
        description="Default task timeout in seconds"
    )
    
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum task retries"
    )
    
    retry_delay: float = Field(
        default=1.0,
        ge=0.1,
        le=60.0,
        description="Retry delay in seconds"
    )


class ProxyConfiguration(UnrealOnBaseModel):
    """Proxy configuration - strictly typed."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    enabled: bool = Field(
        default=False,
        description="Enable proxy usage"
    )
    
    rotation_enabled: bool = Field(
        default=True,
        description="Enable proxy rotation"
    )
    
    rotation_interval: int = Field(
        default=10,
        ge=1,
        le=1000,
        description="Proxy rotation interval (requests)"
    )
    
    health_check_interval: float = Field(
        default=60.0,
        ge=10.0,
        le=3600.0,
        description="Proxy health check interval in seconds"
    )


class DriverConfiguration(UnrealOnBaseModel):
    """Complete driver configuration - strictly typed."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    heartbeat_interval: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Heartbeat interval in seconds"
    )
    
    logging: LoggingConfiguration = Field(
        default_factory=LoggingConfiguration,
        description="Logging configuration"
    )
    
    tasks: TaskConfiguration = Field(
        default_factory=TaskConfiguration,
        description="Task configuration"
    )
    
    proxy: ProxyConfiguration = Field(
        default_factory=ProxyConfiguration,
        description="Proxy configuration"
    )
    
    enabled_managers: List[str] = Field(
        default_factory=lambda: ["logger", "http", "proxy"],
        description="List of enabled managers"
    )


class ConfigurationUpdateData(UnrealOnBaseModel):
    """Configuration update data payload - strictly typed."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    configuration: DriverConfiguration = Field(
        description="Updated configuration parameters"
    )
    
    apply_immediately: bool = Field(
        default=True,
        description="Whether to apply configuration immediately"
    )
    
    restart_required: bool = Field(
        default=False,
        description="Whether driver restart is required"
    )
    
    config_version: Optional[str] = Field(
        default=None,
        description="Configuration version"
    )


class ConfigurationUpdateMessage(WebSocketMessage):
    """Configuration update message (Server → Driver)."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    type: MessageType = Field(
        default=MessageType.COMMAND_CONFIG_UPDATE,
        frozen=True
    )
    
    data: ConfigurationUpdateData = Field(
        description="Configuration update data"
    )
