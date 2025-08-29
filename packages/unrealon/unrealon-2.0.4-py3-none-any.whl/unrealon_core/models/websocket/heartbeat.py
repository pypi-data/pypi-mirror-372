"""
Heartbeat WebSocket Models.

Strictly typed models for driver heartbeat messages.
No raw dictionaries - all data structures are Pydantic models.

Phase 2: Core Systems - WebSocket Bridge
"""

from typing import Optional
from pydantic import Field, ConfigDict

from ..base import UnrealOnBaseModel
from .base import WebSocketMessage, MessageType


class HeartbeatData(UnrealOnBaseModel):
    """Heartbeat data payload - strictly typed."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    driver_status: str = Field(
        default="ready",
        pattern=r"^(ready|busy|idle|error|maintenance)$",
        description="Current driver status"
    )
    
    active_tasks: int = Field(
        default=0,
        ge=0,
        le=1000,
        description="Number of active tasks"
    )
    
    completed_tasks: int = Field(
        default=0,
        ge=0,
        description="Total completed tasks"
    )
    
    failed_tasks: int = Field(
        default=0,
        ge=0,
        description="Total failed tasks"
    )
    
    uptime_seconds: float = Field(
        default=0.0,
        ge=0.0,
        description="Driver uptime in seconds"
    )
    
    memory_usage_mb: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=100000.0,  # 100GB max
        description="Memory usage in MB"
    )
    
    cpu_usage_percent: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="CPU usage percentage"
    )
    
    def get_success_rate(self) -> float:
        """Calculate task success rate."""
        total_tasks = self.completed_tasks + self.failed_tasks
        if total_tasks == 0:
            return 1.0
        return self.completed_tasks / total_tasks
    
    def is_healthy(self) -> bool:
        """Check if driver is healthy."""
        return (
            self.driver_status in ["ready", "busy", "idle"] and
            self.get_success_rate() >= 0.8  # 80% success rate threshold
        )


class HeartbeatMessage(WebSocketMessage):
    """Heartbeat message (Driver → Server)."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    type: MessageType = Field(
        default=MessageType.DRIVER_HEARTBEAT,
        frozen=True
    )
    
    data: HeartbeatData = Field(
        description="Heartbeat data"
    )
