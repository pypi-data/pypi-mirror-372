"""
ARQ Response Models

Strictly typed response models for ARQ job functions.
Following critical requirements - no raw Dict[str, Any].

Phase 2: Core Systems - ARQ Responses
"""

from datetime import datetime
from typing import Optional
from pydantic import Field, ConfigDict

from .base import UnrealOnBaseModel
from ..utils.time import utc_now


class JobResponseBase(UnrealOnBaseModel):
    """Base response model for ARQ jobs."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    success: bool = Field(description="Whether operation succeeded")
    message: str = Field(description="Response message")
    timestamp: datetime = Field(default_factory=utc_now, description="Response timestamp")
    error_code: Optional[str] = Field(default=None, description="Error code if failed")


class TaskAssignmentResponse(JobResponseBase):
    """Response for task assignment job."""
    
    task_id: str = Field(description="Assigned task ID")
    driver_id: str = Field(description="Target driver ID")
    task_type: str = Field(description="Task type")
    priority: str = Field(description="Task priority")


class TaskResultResponse(JobResponseBase):
    """Response for task result processing job."""
    
    task_id: str = Field(description="Task ID")
    driver_id: str = Field(description="Driver ID")
    status: str = Field(description="Task status")
    processing_time: Optional[float] = Field(default=None, description="Processing time in seconds")


class LogEntryResponse(JobResponseBase):
    """Response for log entry processing job."""
    
    driver_id: str = Field(description="Driver ID")
    level: str = Field(description="Log level")
    entries_processed: int = Field(default=1, description="Number of log entries processed")


class DriverRegistrationResponse(JobResponseBase):
    """Response for driver registration job."""
    
    driver_id: str = Field(description="Driver ID")
    driver_type: str = Field(description="Driver type")
    capabilities: list[str] = Field(description="Driver capabilities")
    connection_id: str = Field(description="WebSocket connection ID")


class HeartbeatResponse(JobResponseBase):
    """Response for heartbeat processing job."""
    
    driver_id: str = Field(description="Driver ID")
    status: str = Field(description="Driver status")
    is_healthy: bool = Field(description="Whether driver is healthy")
    success_rate: Optional[float] = Field(default=None, description="Driver success rate")


class ConfigurationUpdateResponse(JobResponseBase):
    """Response for configuration update job."""
    
    driver_id: str = Field(description="Driver ID")
    configuration_applied: bool = Field(description="Whether configuration was applied")
    restart_required: bool = Field(default=False, description="Whether restart is required")


class PingResponse(JobResponseBase):
    """Response for ping job."""
    
    pong_timestamp: datetime = Field(description="Pong timestamp")
    latency_ms: Optional[float] = Field(default=None, description="Latency in milliseconds")


class DriverStatusResponse(JobResponseBase):
    """Response for driver status query."""
    
    driver_id: str = Field(description="Driver ID")
    status: str = Field(description="Driver status")
    last_seen: Optional[datetime] = Field(default=None, description="Last seen timestamp")
    active_tasks: int = Field(default=0, description="Number of active tasks")


class DriverListResponse(JobResponseBase):
    """Response for driver list query."""
    
    drivers: list["DriverInfo"] = Field(description="List of available drivers")
    total_count: int = Field(description="Total number of drivers")
    filter_applied: Optional[str] = Field(default=None, description="Filter that was applied")


class DriverInfo(UnrealOnBaseModel):
    """Driver information for list response."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    driver_id: str = Field(description="Driver ID")
    driver_type: str = Field(description="Driver type")
    status: str = Field(description="Driver status")
    capabilities: list[str] = Field(description="Driver capabilities")
    last_seen: Optional[datetime] = Field(default=None, description="Last seen timestamp")
    active_tasks: int = Field(default=0, description="Number of active tasks")


# Update forward references
DriverListResponse.model_rebuild()
