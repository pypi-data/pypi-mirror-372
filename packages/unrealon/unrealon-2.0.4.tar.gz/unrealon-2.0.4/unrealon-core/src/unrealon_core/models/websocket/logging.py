"""
Logging WebSocket Models.

Strictly typed models for log entries and batches.
No raw dictionaries - all data structures are Pydantic models.

Phase 2: Core Systems - WebSocket Bridge
"""

from typing import List, Optional
from pydantic import Field, ConfigDict, field_validator

from ..base import UnrealOnBaseModel
from .base import WebSocketMessage, MessageType


class LogContext(UnrealOnBaseModel):
    """Log context data - strictly typed for centralized logging."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    # Task context
    task_id: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Associated task ID"
    )
    
    url: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Associated URL"
    )
    
    # Performance metrics
    duration_ms: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Operation duration in milliseconds"
    )
    
    memory_usage_mb: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Memory usage in MB"
    )
    
    cpu_usage_percent: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="CPU usage percentage"
    )
    
    # Error context
    error_code: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Error code if applicable"
    )
    
    stack_trace: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Stack trace for errors"
    )
    
    # Network context
    user_agent: Optional[str] = Field(
        default=None,
        max_length=500,
        description="User agent used"
    )
    
    proxy_id: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Proxy ID used"
    )
    
    response_code: Optional[int] = Field(
        default=None,
        ge=100,
        le=599,
        description="HTTP response code"
    )
    
    # Driver context
    driver_version: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Driver version"
    )
    
    session_id: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Driver session ID"
    )


class LogEntryData(UnrealOnBaseModel):
    """Log entry data payload - strictly typed for centralized logging."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    # Core log fields
    level: str = Field(
        pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Log level"
    )
    
    message: str = Field(
        min_length=1,
        max_length=2000,
        description="Log message"
    )
    
    timestamp: str = Field(
        description="Log timestamp in ISO format"
    )
    
    # Source identification
    logger_name: str = Field(
        default="driver",
        min_length=1,
        max_length=100,
        description="Logger name"
    )
    
    module: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Module that generated the log"
    )
    
    function_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Function that generated the log"
    )
    
    line_number: Optional[int] = Field(
        default=None,
        ge=1,
        description="Line number where log was generated"
    )
    
    # Driver identification
    driver_id: str = Field(
        min_length=1,
        max_length=100,
        description="Unique driver identifier"
    )
    
    driver_type: str = Field(
        default="unrealon_driver",
        max_length=50,
        description="Type of driver"
    )
    
    # Environment
    environment: str = Field(
        default="production",
        pattern=r"^(development|staging|production)$",
        description="Environment where log was generated"
    )
    
    # Rich context
    context: LogContext = Field(
        default_factory=LogContext,
        description="Additional log context"
    )
    
    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate ISO timestamp format."""
        from datetime import datetime
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError("timestamp must be valid ISO format")


class LogEntryMessage(WebSocketMessage):
    """Log entry message (Driver → Server)."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    type: MessageType = Field(
        default=MessageType.LOG_MESSAGE,
        frozen=True
    )
    
    data: LogEntryData = Field(
        description="Log entry data"
    )


class LogBatchData(UnrealOnBaseModel):
    """Log batch data payload - strictly typed."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    logs: List[LogEntryData] = Field(
        min_length=1,
        max_length=100,
        description="Batch of log entries"
    )
    
    driver_id: str = Field(
        min_length=1,
        description="Driver ID for the batch"
    )
    
    batch_timestamp: str = Field(
        description="Timestamp when batch was created (ISO format)"
    )
    
    @field_validator('batch_timestamp')
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate ISO timestamp format."""
        from datetime import datetime
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError("batch_timestamp must be valid ISO format")


class LogBatchMessage(WebSocketMessage):
    """Log batch message (Driver → Server)."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    type: MessageType = Field(
        default=MessageType.LOG_BATCH,
        frozen=True
    )
    
    data: LogBatchData = Field(
        description="Log batch data"
    )
