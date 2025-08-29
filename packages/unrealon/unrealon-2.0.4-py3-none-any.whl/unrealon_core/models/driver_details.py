"""
Driver Details Models

Strictly typed models for driver information and statistics.
Following critical requirements - no raw Dict[str, Any].

Phase 2: Core Systems - Driver Details
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from .base import UnrealOnBaseModel


class DriverDetails(UnrealOnBaseModel):
    """Complete driver details with statistics."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    # Basic driver info
    driver_id: str = Field(description="Driver ID")
    driver_name: Optional[str] = Field(default=None, description="Driver name")
    driver_type: str = Field(description="Driver type")
    capabilities: List[str] = Field(default_factory=list, description="Driver capabilities")
    version: Optional[str] = Field(default=None, description="Driver version")
    
    # Connection info
    connection_id: str = Field(description="WebSocket connection ID")
    status: str = Field(description="Driver status")
    connected_at: datetime = Field(description="Connection timestamp")
    last_seen: datetime = Field(description="Last activity timestamp")
    
    # Task statistics
    active_tasks: int = Field(default=0, description="Number of active tasks")
    completed_tasks: int = Field(default=0, description="Number of completed tasks")
    failed_tasks: int = Field(default=0, description="Number of failed tasks")
    
    # Performance metrics
    uptime_seconds: float = Field(default=0.0, description="Uptime in seconds")
    memory_usage_mb: Optional[float] = Field(default=None, description="Memory usage in MB")
    cpu_usage_percent: Optional[float] = Field(default=None, description="CPU usage percentage")


class DriverInfo(UnrealOnBaseModel):
    """Basic driver information."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    driver_id: str = Field(description="Driver ID")
    connection_id: str = Field(description="WebSocket connection ID")
    status: str = Field(description="Driver status")
    last_heartbeat: Optional[datetime] = Field(default=None, description="Last heartbeat timestamp")


class DriverListResult(UnrealOnBaseModel):
    """Result of driver list query."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    drivers: List[DriverDetails] = Field(description="List of driver details")
    total_count: int = Field(description="Total number of drivers")
    filtered_count: int = Field(description="Number of drivers after filtering")
    filter_applied: Optional[str] = Field(default=None, description="Filter that was applied")


def create_driver_details_from_session(
    driver_info: DriverInfo,
    session: "DriverSession"
) -> DriverDetails:
    """Create DriverDetails from DriverInfo and DriverSession."""
    return DriverDetails(
        driver_id=driver_info.driver_id,
        driver_name=getattr(session, 'driver_name', None),
        driver_type=session.driver_type,
        capabilities=session.capabilities,
        version=getattr(session, 'version', None),
        connection_id=session.connection_id,
        status=session.status,
        connected_at=session.connected_at,
        last_seen=session.last_seen,
        active_tasks=session.active_tasks,
        completed_tasks=getattr(session, 'completed_tasks', 0),
        failed_tasks=getattr(session, 'failed_tasks', 0),
        uptime_seconds=(utc_now() - session.connected_at).total_seconds(),
        memory_usage_mb=getattr(session, 'memory_usage_mb', None),
        cpu_usage_percent=getattr(session, 'cpu_usage_percent', None)
    )
