"""
ARQ Context Models

Strictly typed models for ARQ worker context and job parameters.
Following critical requirements - no raw Dict[str, Any].

Phase 2: Core Systems - ARQ Context
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from .base import UnrealOnBaseModel


class ARQWorkerStats(UnrealOnBaseModel):
    """ARQ worker statistics."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    processed_jobs: int = Field(default=0, description="Number of processed jobs")
    failed_jobs: int = Field(default=0, description="Number of failed jobs")
    start_time: datetime = Field(description="Worker start time")
    websocket_messages_sent: int = Field(default=0, description="WebSocket messages sent")
    websocket_messages_failed: int = Field(default=0, description="Failed WebSocket messages")


class ARQWorkerContext(UnrealOnBaseModel):
    """ARQ worker context with strict typing."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    stats: ARQWorkerStats = Field(description="Worker statistics")
    websocket_bridge: Optional[object] = Field(default=None, description="WebSocket bridge instance")


class TaskAssignmentParams(UnrealOnBaseModel):
    """Parameters for task assignment job."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    task_type: str = Field(description="Type of task")
    task_data: "TaskDataModel" = Field(description="Task data")
    driver_id: Optional[str] = Field(default=None, description="Target driver ID")
    priority: str = Field(default="normal", description="Task priority")
    timeout: float = Field(default=300.0, description="Task timeout in seconds")
    retry_count: int = Field(default=3, description="Number of retries")


class TaskDataModel(UnrealOnBaseModel):
    """Strictly typed task data."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    task_id: str = Field(description="Unique task identifier")
    url: str = Field(description="Target URL")
    parser_type: Optional[str] = Field(default=None, description="Parser type")
    options: Optional["TaskOptionsModel"] = Field(default=None, description="Task options")


class TaskOptionsModel(UnrealOnBaseModel):
    """Task options model."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    timeout_seconds: Optional[float] = Field(default=None, description="Request timeout")
    user_agent: Optional[str] = Field(default=None, description="User agent string")
    headers: Optional["HeadersModel"] = Field(default=None, description="HTTP headers")
    proxy_enabled: bool = Field(default=True, description="Whether to use proxy")


class HeadersModel(UnrealOnBaseModel):
    """HTTP headers model."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    accept: Optional[str] = Field(default=None, description="Accept header")
    accept_language: Optional[str] = Field(default=None, description="Accept-Language header")
    referer: Optional[str] = Field(default=None, description="Referer header")
    authorization: Optional[str] = Field(default=None, description="Authorization header")


class TaskResultParams(UnrealOnBaseModel):
    """Parameters for task result processing."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    driver_id: str = Field(description="Driver ID")
    connection_id: str = Field(description="WebSocket connection ID")
    result_data: "TaskResultDataModel" = Field(description="Task result data")


class TaskResultDataModel(UnrealOnBaseModel):
    """Task result data model."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    task_id: str = Field(description="Task ID")
    status: str = Field(description="Task status")
    result_data: Optional["ParsedDataModel"] = Field(default=None, description="Parsed data")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    execution_time_seconds: float = Field(description="Execution time")


class ParsedDataModel(UnrealOnBaseModel):
    """Parsed data model."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    title: Optional[str] = Field(default=None, description="Page title")
    content: Optional[str] = Field(default=None, description="Page content")
    links: Optional[list[str]] = Field(default=None, description="Extracted links")
    images: Optional[list[str]] = Field(default=None, description="Extracted images")
    metadata: Optional["MetadataModel"] = Field(default=None, description="Page metadata")


class MetadataModel(UnrealOnBaseModel):
    """Page metadata model."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    description: Optional[str] = Field(default=None, description="Page description")
    keywords: Optional[str] = Field(default=None, description="Page keywords")
    author: Optional[str] = Field(default=None, description="Page author")
    language: Optional[str] = Field(default=None, description="Page language")


class LogEntryParams(UnrealOnBaseModel):
    """Parameters for log entry processing."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    driver_id: str = Field(description="Driver ID")
    connection_id: str = Field(description="WebSocket connection ID")
    log_data: "LogDataModel" = Field(description="Log data")


class LogDataModel(UnrealOnBaseModel):
    """Log data model."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    level: str = Field(description="Log level")
    message: str = Field(description="Log message")
    logger_name: str = Field(description="Logger name")
    module: str = Field(description="Module name")
    timestamp: datetime = Field(description="Log timestamp")


class DriverRegistrationParams(UnrealOnBaseModel):
    """Parameters for driver registration."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    connection_id: str = Field(description="WebSocket connection ID")
    driver_data: "DriverDataModel" = Field(description="Driver data")


class DriverDataModel(UnrealOnBaseModel):
    """Driver data model."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    driver_id: str = Field(description="Driver ID")
    driver_type: str = Field(description="Driver type")
    version: str = Field(description="Driver version")
    capabilities: list[str] = Field(description="Driver capabilities")


class HeartbeatParams(UnrealOnBaseModel):
    """Parameters for heartbeat processing."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    driver_id: str = Field(description="Driver ID")
    connection_id: str = Field(description="WebSocket connection ID")
    heartbeat_data: "HeartbeatDataModel" = Field(description="Heartbeat data")


class HeartbeatDataModel(UnrealOnBaseModel):
    """Heartbeat data model."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    driver_id: str = Field(description="Driver ID")
    driver_status: str = Field(description="Driver status")
    cpu_usage: float = Field(description="CPU usage percentage")
    memory_usage: float = Field(description="Memory usage in MB")
    active_tasks: int = Field(description="Number of active tasks")
    completed_tasks: int = Field(description="Number of completed tasks")
    failed_tasks: int = Field(description="Number of failed tasks")


# Update forward references
TaskAssignmentParams.model_rebuild()
TaskDataModel.model_rebuild()
TaskOptionsModel.model_rebuild()
TaskResultParams.model_rebuild()
TaskResultDataModel.model_rebuild()
ParsedDataModel.model_rebuild()
LogEntryParams.model_rebuild()
DriverRegistrationParams.model_rebuild()
HeartbeatParams.model_rebuild()
