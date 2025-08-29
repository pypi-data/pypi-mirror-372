"""
Bridge Statistics Models

Strictly typed models for WebSocket bridge statistics.
Following critical requirements - no raw Dict[str, Any].

Phase 2: Core Systems - Bridge Statistics
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from .base import UnrealOnBaseModel
from ..utils.time import utc_now


class BridgeStatsData(UnrealOnBaseModel):
    """Internal bridge statistics data."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    tasks_sent: int = Field(default=0, description="Number of tasks sent")
    tasks_failed: int = Field(default=0, description="Number of tasks failed")
    configs_sent: int = Field(default=0, description="Number of configurations sent")
    configs_failed: int = Field(default=0, description="Number of configurations failed")
    messages_processed: int = Field(default=0, description="Number of messages processed")
    start_time: str = Field(description="Start time ISO string")
    
    def increment_tasks_sent(self) -> None:
        """Increment tasks sent counter."""
        self.tasks_sent += 1
    
    def increment_tasks_failed(self) -> None:
        """Increment tasks failed counter."""
        self.tasks_failed += 1
    
    def increment_configs_sent(self) -> None:
        """Increment configs sent counter."""
        self.configs_sent += 1
    
    def increment_configs_failed(self) -> None:
        """Increment configs failed counter."""
        self.configs_failed += 1
    
    def increment_messages_processed(self) -> None:
        """Increment messages processed counter."""
        self.messages_processed += 1


def create_initial_bridge_stats() -> BridgeStatsData:
    """Create initial bridge statistics."""
    return BridgeStatsData(
        start_time=utc_now().isoformat()
    )
