"""
WebSocket Session Models

Strictly typed models for WebSocket session management.
Following critical requirements - no raw Dict[str, Any].

Phase 2: Core Systems - WebSocket Session
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from .base import UnrealOnBaseModel


class DriverSession(UnrealOnBaseModel):
    """Driver WebSocket session information."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    driver_id: str = Field(description="Driver ID")
    driver_type: str = Field(description="Driver type")
    connection_id: str = Field(description="WebSocket connection ID")
    connected_at: datetime = Field(description="Connection timestamp")
    last_seen: datetime = Field(description="Last activity timestamp")
    capabilities: List[str] = Field(description="Driver capabilities")
    status: str = Field(default="connected", description="Connection status")
    active_tasks: int = Field(default=0, description="Number of active tasks")


class ConnectionStats(UnrealOnBaseModel):
    """WebSocket connection statistics."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    total_connections: int = Field(description="Total connections made")
    active_connections: int = Field(description="Currently active connections")
    messages_sent: int = Field(description="Total messages sent")
    messages_received: int = Field(description="Total messages received")
    errors: int = Field(description="Number of errors")
    uptime_seconds: float = Field(description="Server uptime in seconds")


class BridgeStats(UnrealOnBaseModel):
    """WebSocket bridge statistics."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    active_connections: int = Field(description="Active WebSocket connections")
    total_messages: int = Field(description="Total messages processed")
    arq_jobs_sent: int = Field(description="ARQ jobs sent")
    arq_jobs_failed: int = Field(description="ARQ jobs failed")
    registered_drivers: int = Field(description="Number of registered drivers")
    uptime_seconds: float = Field(description="Bridge uptime in seconds")


class ConfigurationData(UnrealOnBaseModel):
    """Configuration data for drivers."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    log_level: Optional[str] = Field(default=None, description="Logging level")
    batch_size: Optional[int] = Field(default=None, description="Batch size for operations")
    timeout_seconds: Optional[float] = Field(default=None, description="Operation timeout")
    proxy_enabled: Optional[bool] = Field(default=None, description="Whether proxy is enabled")
    max_retries: Optional[int] = Field(default=None, description="Maximum retry attempts")


class ComponentDetails(UnrealOnBaseModel):
    """Component details for dashboard."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    name: str = Field(description="Component name")
    timestamp: str = Field(description="Timestamp ISO string")
    health: Optional["ComponentHealth"] = Field(default=None, description="Health information")
    metrics: "ComponentMetrics" = Field(description="Component metrics")
    alerts: List["ComponentAlert"] = Field(description="Component alerts")


class ComponentHealth(UnrealOnBaseModel):
    """Component health information."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    status: str = Field(description="Health status")
    last_check: str = Field(description="Last check timestamp")
    uptime_seconds: float = Field(description="Uptime in seconds")
    failure_rate: float = Field(description="Failure rate percentage")
    check_count: int = Field(description="Total health checks")


class ComponentMetrics(UnrealOnBaseModel):
    """Component metrics information."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    metric_name: str = Field(description="Metric name")
    metric_type: str = Field(description="Metric type")
    current_value: float = Field(description="Current value")
    total_samples: int = Field(description="Total samples")
    last_updated: str = Field(description="Last updated timestamp")


class ComponentAlert(UnrealOnBaseModel):
    """Component alert information."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    alert_id: str = Field(description="Alert ID")
    rule_name: str = Field(description="Alert rule name")
    severity: str = Field(description="Alert severity")
    message: str = Field(description="Alert message")
    timestamp: str = Field(description="Alert timestamp")
    component_name: Optional[str] = Field(default=None, description="Related component")


# Update forward references
ComponentDetails.model_rebuild()
