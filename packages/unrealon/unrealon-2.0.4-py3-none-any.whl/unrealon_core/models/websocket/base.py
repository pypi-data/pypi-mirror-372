"""
Base WebSocket Models.

Core message types and base classes for WebSocket communication.
Strictly typed without raw dictionaries.

Phase 2: Core Systems - WebSocket Bridge
"""

from typing import Optional
from datetime import datetime

from pydantic import Field, ConfigDict, field_serializer
from ..base import UnrealOnBaseModel, TimestampedModel, IdentifiedModel
from ...enums.types import MessageType
from ...utils.time import datetime_to_iso


class WebSocketMessage(IdentifiedModel, TimestampedModel):
    """
    Base WebSocket message model.
    
    All WebSocket messages inherit from this base class for consistency.
    Provides message ID, timestamp, and optional correlation ID.
    
    CRITICAL: No raw Dict[str, Any] - all data must be typed!
    """
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        use_enum_values=True
    )
    
    type: MessageType = Field(
        description="Type of the WebSocket message"
    )
    
    correlation_id: Optional[str] = Field(
        default=None,
        description="ID of the message this is responding to"
    )
    
    @field_serializer('created_at', 'updated_at', when_used='json')
    def serialize_datetime_fields(self, value: Optional[datetime]) -> Optional[str]:
        """Serialize datetime fields to ISO format."""
        return datetime_to_iso(value)
    

