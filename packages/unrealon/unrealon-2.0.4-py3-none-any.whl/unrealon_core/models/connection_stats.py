"""
Connection Statistics Models

Strictly typed models for WebSocket connection statistics.
Following critical requirements - no raw Dict[str, Any].

Phase 2: Core Systems - Connection Statistics
"""

from pydantic import BaseModel, Field, ConfigDict

from .base import UnrealOnBaseModel


class ConnectionStatsData(UnrealOnBaseModel):
    """Internal connection statistics data."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    total_connections: int = Field(default=0, description="Total connections made")
    active_connections: int = Field(default=0, description="Currently active connections")
    total_messages: int = Field(default=0, description="Total messages sent")
    failed_messages: int = Field(default=0, description="Failed messages")
    
    def increment_total_connections(self) -> None:
        """Increment total connections counter."""
        self.total_connections += 1
    
    def set_active_connections(self, count: int) -> None:
        """Set active connections count."""
        self.active_connections = count
    
    def increment_total_messages(self) -> None:
        """Increment total messages counter."""
        self.total_messages += 1
    
    def increment_failed_messages(self) -> None:
        """Increment failed messages counter."""
        self.failed_messages += 1


def create_initial_connection_stats() -> ConnectionStatsData:
    """Create initial connection statistics."""
    return ConnectionStatsData()
