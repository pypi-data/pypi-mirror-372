"""
Error and Acknowledgment WebSocket Models.

Strictly typed models for error messages and acknowledgments.
No raw dictionaries - all data structures are Pydantic models.

Phase 2: Core Systems - WebSocket Bridge
"""

from typing import Optional, List
from pydantic import Field, ConfigDict

from ..base import UnrealOnBaseModel
from .base import WebSocketMessage, MessageType


class ErrorDetails(UnrealOnBaseModel):
    """Error details - strictly typed."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    field_errors: List[str] = Field(
        default_factory=list,
        description="Field validation errors"
    )
    
    stack_trace: Optional[str] = Field(
        default=None,
        description="Stack trace (if available)"
    )
    
    request_id: Optional[str] = Field(
        default=None,
        description="Request ID that caused the error"
    )
    
    timestamp: Optional[str] = Field(
        default=None,
        description="Error timestamp"
    )


class ErrorData(UnrealOnBaseModel):
    """Error data payload - strictly typed."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    error_code: str = Field(
        min_length=1,
        max_length=100,
        description="Error code identifier"
    )
    
    error_message: str = Field(
        min_length=1,
        max_length=1000,
        description="Human-readable error message"
    )
    
    details: Optional[ErrorDetails] = Field(
        default=None,
        description="Additional error details"
    )
    
    retry_after: Optional[int] = Field(
        default=None,
        ge=0,
        le=3600,
        description="Retry after seconds (if retryable)"
    )


class ErrorMessage(WebSocketMessage):
    """Error message (Bidirectional)."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    type: MessageType = Field(
        default=MessageType.ERROR,
        frozen=True
    )
    
    data: ErrorData = Field(
        description="Error data"
    )


class AckData(UnrealOnBaseModel):
    """Acknowledgment data payload - strictly typed."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    acknowledged: bool = Field(
        default=True,
        description="Acknowledgment status"
    )
    
    message: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional acknowledgment message"
    )
    
    processing_time_ms: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Processing time in milliseconds"
    )


class AckMessage(WebSocketMessage):
    """Acknowledgment message (Bidirectional)."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    type: MessageType = Field(
        default=MessageType.ACK,
        frozen=True
    )
    
    data: AckData = Field(
        description="Acknowledgment data"
    )
