"""
WebSocket Message Utilities.

Utility functions for creating WebSocket messages.
Strictly typed - no raw dictionaries.

Phase 2: Core Systems - WebSocket Bridge
"""

from typing import Optional, List
from datetime import datetime

from .errors import ErrorMessage, ErrorData, ErrorDetails, AckMessage, AckData
from ...utils.time import utc_now


def create_error_message(
    error_code: str,
    error_message: str,
    correlation_id: Optional[str] = None,
    field_errors: Optional[List[str]] = None,
    stack_trace: Optional[str] = None,
    retry_after: Optional[int] = None
) -> ErrorMessage:
    """
    Create an error message with strict typing.
    
    Args:
        error_code: Error code identifier
        error_message: Human-readable error message
        correlation_id: ID of the message this is responding to
        field_errors: List of field validation errors
        stack_trace: Stack trace if available
        retry_after: Retry after seconds if retryable
        
    Returns:
        Strictly typed ErrorMessage
    """
    details = None
    if field_errors or stack_trace:
        details = ErrorDetails(
            field_errors=field_errors or [],
            stack_trace=stack_trace,
            timestamp=utc_now().isoformat()
        )
    
    error_data = ErrorData(
        error_code=error_code,
        error_message=error_message,
        details=details,
        retry_after=retry_after
    )
    
    return ErrorMessage(
        correlation_id=correlation_id,
        data=error_data
    )


def create_ack_message(
    correlation_id: str,
    message: Optional[str] = None,
    processing_time_ms: Optional[float] = None
) -> AckMessage:
    """
    Create an acknowledgment message with strict typing.
    
    Args:
        correlation_id: ID of the message being acknowledged
        message: Optional acknowledgment message
        processing_time_ms: Processing time in milliseconds
        
    Returns:
        Strictly typed AckMessage
    """
    ack_data = AckData(
        acknowledged=True,
        message=message,
        processing_time_ms=processing_time_ms
    )
    
    return AckMessage(
        correlation_id=correlation_id,
        data=ack_data
    )


def create_validation_error_message(
    validation_errors: List[str],
    correlation_id: Optional[str] = None
) -> ErrorMessage:
    """
    Create a validation error message.
    
    Args:
        validation_errors: List of validation error messages
        correlation_id: ID of the message this is responding to
        
    Returns:
        Strictly typed ErrorMessage for validation errors
    """
    return create_error_message(
        error_code="VALIDATION_ERROR",
        error_message="Message validation failed",
        correlation_id=correlation_id,
        field_errors=validation_errors
    )


def create_timeout_error_message(
    operation: str,
    timeout_seconds: float,
    correlation_id: Optional[str] = None
) -> ErrorMessage:
    """
    Create a timeout error message.
    
    Args:
        operation: Operation that timed out
        timeout_seconds: Timeout duration
        correlation_id: ID of the message this is responding to
        
    Returns:
        Strictly typed ErrorMessage for timeout errors
    """
    return create_error_message(
        error_code="TIMEOUT_ERROR",
        error_message=f"Operation '{operation}' timed out after {timeout_seconds} seconds",
        correlation_id=correlation_id,
        retry_after=int(timeout_seconds * 2)  # Suggest retry after double the timeout
    )


def create_connection_error_message(
    reason: str,
    correlation_id: Optional[str] = None
) -> ErrorMessage:
    """
    Create a connection error message.
    
    Args:
        reason: Connection error reason
        correlation_id: ID of the message this is responding to
        
    Returns:
        Strictly typed ErrorMessage for connection errors
    """
    return create_error_message(
        error_code="CONNECTION_ERROR",
        error_message=f"Connection error: {reason}",
        correlation_id=correlation_id,
        retry_after=30  # Suggest retry after 30 seconds
    )
