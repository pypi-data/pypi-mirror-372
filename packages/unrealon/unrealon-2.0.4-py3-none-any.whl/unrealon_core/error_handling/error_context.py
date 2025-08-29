"""
Error Context System

Rich error context for debugging and monitoring.
Following critical requirements - max 500 lines, functions < 20 lines.

Phase 2: Core Systems - Error Handling
"""

import traceback
from datetime import datetime
from typing import Any, Dict, Optional, List
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict

from ..utils.time import utc_now


class ErrorSeverity(str, Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorContext(BaseModel):
    """Rich error context information."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    # Basic error info
    error_id: str = Field(description="Unique error identifier")
    error_type: str = Field(description="Error class name")
    error_message: str = Field(description="Error message")
    severity: ErrorSeverity = Field(description="Error severity level")
    
    # Timing
    timestamp: datetime = Field(description="When error occurred")
    duration_ms: Optional[float] = Field(default=None, description="Operation duration before error")
    
    # Context
    operation: str = Field(description="Operation that failed")
    component: str = Field(description="Component where error occurred")
    user_id: Optional[str] = Field(default=None, description="Associated user ID")
    request_id: Optional[str] = Field(default=None, description="Request correlation ID")
    
    # Technical details
    stack_trace: Optional[str] = Field(default=None, description="Full stack trace")
    function_name: str = Field(description="Function where error occurred")
    file_name: str = Field(description="File where error occurred")
    line_number: int = Field(description="Line number where error occurred")
    
    # Additional context
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Function parameters")
    environment: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Recovery info
    is_retryable: bool = Field(default=True, description="Whether error is retryable")
    retry_count: int = Field(default=0, description="Number of retries attempted")
    recovery_suggestions: List[str] = Field(default_factory=list, description="Recovery suggestions")


def create_error_context(
    error: Exception,
    operation: str,
    component: str,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    **kwargs
) -> ErrorContext:
    """
    Create error context from exception.
    
    Args:
        error: Exception that occurred
        operation: Operation that failed
        component: Component where error occurred
        severity: Error severity level
        **kwargs: Additional context data
        
    Returns:
        ErrorContext with rich error information
    """
    import uuid
    import inspect
    import os
    
    # Get stack trace info
    tb = traceback.extract_tb(error.__traceback__)
    if tb:
        frame = tb[-1]  # Last frame (where error occurred)
        file_name = os.path.basename(frame.filename)
        function_name = frame.name
        line_number = frame.lineno
    else:
        file_name = "unknown"
        function_name = "unknown"
        line_number = 0
    
    # Generate error ID
    error_id = str(uuid.uuid4())[:8]
    
    # Extract parameters from current frame
    parameters = {}
    try:
        frame = inspect.currentframe()
        if frame and frame.f_back:
            parameters = {
                k: str(v) for k, v in frame.f_back.f_locals.items()
                if not k.startswith('_') and not callable(v)
            }
    except Exception:
        pass  # Ignore parameter extraction errors
    
    # Basic environment info
    environment = {
        'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
        'platform': os.sys.platform,
    }
    
    return ErrorContext(
        error_id=error_id,
        error_type=error.__class__.__name__,
        error_message=str(error),
        severity=severity,
        timestamp=utc_now(),
        operation=operation,
        component=component,
        stack_trace=traceback.format_exc(),
        function_name=function_name,
        file_name=file_name,
        line_number=line_number,
        parameters=parameters,
        environment=environment,
        **kwargs
    )


def format_error_context(context: ErrorContext, include_stack_trace: bool = False) -> str:
    """
    Format error context for logging.
    
    Args:
        context: Error context to format
        include_stack_trace: Whether to include full stack trace
        
    Returns:
        Formatted error message
    """
    lines = [
        f"🚨 ERROR [{context.error_id}] {context.severity.upper()}",
        f"   Type: {context.error_type}",
        f"   Message: {context.error_message}",
        f"   Operation: {context.operation}",
        f"   Component: {context.component}",
        f"   Location: {context.file_name}:{context.line_number} in {context.function_name}()",
        f"   Time: {context.timestamp.isoformat()}",
    ]
    
    if context.duration_ms:
        lines.append(f"   Duration: {context.duration_ms:.2f}ms")
    
    if context.request_id:
        lines.append(f"   Request ID: {context.request_id}")
    
    if context.user_id:
        lines.append(f"   User ID: {context.user_id}")
    
    if context.retry_count > 0:
        lines.append(f"   Retries: {context.retry_count}")
    
    if context.parameters:
        lines.append("   Parameters:")
        for key, value in context.parameters.items():
            lines.append(f"     {key}: {value}")
    
    if context.recovery_suggestions:
        lines.append("   Recovery suggestions:")
        for suggestion in context.recovery_suggestions:
            lines.append(f"     • {suggestion}")
    
    if include_stack_trace and context.stack_trace:
        lines.append("   Stack trace:")
        for line in context.stack_trace.split('\n'):
            if line.strip():
                lines.append(f"     {line}")
    
    return '\n'.join(lines)


def determine_severity(error: Exception) -> ErrorSeverity:
    """
    Determine error severity based on exception type.
    
    Args:
        error: Exception to analyze
        
    Returns:
        Appropriate severity level
    """
    error_name = error.__class__.__name__
    
    # Critical errors
    critical_errors = [
        'SystemError', 'MemoryError', 'KeyboardInterrupt',
        'SystemExit', 'GeneratorExit'
    ]
    
    # High severity errors
    high_errors = [
        'ConnectionError', 'DatabaseError', 'AuthenticationError',
        'PermissionError', 'SecurityError'
    ]
    
    # Medium severity errors
    medium_errors = [
        'ValidationError', 'ValueError', 'TypeError',
        'AttributeError', 'KeyError', 'IndexError'
    ]
    
    if error_name in critical_errors:
        return ErrorSeverity.CRITICAL
    elif error_name in high_errors:
        return ErrorSeverity.HIGH
    elif error_name in medium_errors:
        return ErrorSeverity.MEDIUM
    else:
        return ErrorSeverity.LOW


def is_retryable_error(error: Exception) -> bool:
    """
    Determine if error is retryable.
    
    Args:
        error: Exception to analyze
        
    Returns:
        True if error should be retried
    """
    error_name = error.__class__.__name__
    
    # Non-retryable errors
    non_retryable = [
        'ValidationError', 'ValueError', 'TypeError',
        'AttributeError', 'KeyError', 'IndexError',
        'AuthenticationError', 'PermissionError',
        'NotImplementedError', 'AssertionError'
    ]
    
    # Retryable errors
    retryable = [
        'ConnectionError', 'TimeoutError', 'HTTPError',
        'NetworkError', 'ServiceUnavailableError',
        'TemporaryError', 'RateLimitError'
    ]
    
    if error_name in non_retryable:
        return False
    elif error_name in retryable:
        return True
    else:
        # Default to retryable for unknown errors
        return True


def get_recovery_suggestions(error: Exception, operation: str) -> List[str]:
    """
    Get recovery suggestions for error.
    
    Args:
        error: Exception that occurred
        operation: Operation that failed
        
    Returns:
        List of recovery suggestions
    """
    error_name = error.__class__.__name__
    suggestions = []
    
    if error_name == 'ConnectionError':
        suggestions.extend([
            "Check network connectivity",
            "Verify service endpoint is accessible",
            "Check firewall settings"
        ])
    
    elif error_name == 'TimeoutError':
        suggestions.extend([
            "Increase timeout value",
            "Check service performance",
            "Retry with exponential backoff"
        ])
    
    elif error_name == 'ValidationError':
        suggestions.extend([
            "Check input data format",
            "Verify required fields are present",
            "Review data validation rules"
        ])
    
    elif error_name == 'AuthenticationError':
        suggestions.extend([
            "Check authentication credentials",
            "Verify token is not expired",
            "Refresh authentication token"
        ])
    
    elif error_name == 'PermissionError':
        suggestions.extend([
            "Check user permissions",
            "Verify access rights for operation",
            "Contact administrator for access"
        ])
    
    else:
        suggestions.append(f"Review {operation} implementation")
    
    return suggestions
