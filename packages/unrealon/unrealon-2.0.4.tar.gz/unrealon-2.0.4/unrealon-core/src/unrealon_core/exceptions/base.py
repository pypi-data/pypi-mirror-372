"""
Base exceptions for UnrealOn system.

Provides the foundation exception classes that all other
UnrealOn exceptions inherit from. Includes error codes,
context information, and structured error handling.

Phase 1: Foundation exception hierarchy
"""

from typing import Optional, Dict, Any, Union
from unrealon_core.utils.time import utc_now

class UnrealOnError(Exception):
    """
    Base exception for all UnrealOn errors.
    
    Provides:
    - Error codes for programmatic handling
    - Context information for debugging
    - Structured error data
    - Timestamp tracking
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Initialize UnrealOn error.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            context: Additional context information
            cause: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self._get_default_error_code()
        self.context = context or {}
        self.cause = cause
        self.timestamp = utc_now()
        
        # Set the cause for proper exception chaining
        if cause:
            self.__cause__ = cause
    
    def _get_default_error_code(self) -> str:
        """Get default error code based on exception class name."""
        class_name = self.__class__.__name__
        # Convert CamelCase to UPPER_SNAKE_CASE
        import re
        error_code = re.sub('([a-z0-9])([A-Z])', r'\1_\2', class_name).upper()
        return error_code
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        return {
            'error_type': self.__class__.__name__,
            'error_code': self.error_code,
            'message': self.message,
            'context': self.context,
            'timestamp': self.timestamp.isoformat(),
            'cause': str(self.cause) if self.cause else None
        }
    
    def add_context(self, key: str, value: Any) -> 'UnrealOnError':
        """Add context information to the error."""
        self.context[key] = value
        return self
    
    def with_context(self, **context) -> 'UnrealOnError':
        """Add multiple context items to the error."""
        self.context.update(context)
        return self
    
    def __str__(self) -> str:
        """String representation of the error."""
        parts = [f"[{self.error_code}] {self.message}"]
        
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            parts.append(f"Context: {context_str}")
        
        if self.cause:
            parts.append(f"Caused by: {self.cause}")
        
        return " | ".join(parts)
    
    def __repr__(self) -> str:
        """Detailed representation of the error."""
        return (
            f"{self.__class__.__name__}("
            f"message='{self.message}', "
            f"error_code='{self.error_code}', "
            f"context={self.context}, "
            f"cause={self.cause!r})"
        )


class UnrealOnWarning(UserWarning):
    """
    Base warning for UnrealOn system.
    
    Used for non-fatal issues that should be logged
    but don't prevent operation from continuing.
    """
    
    def __init__(
        self,
        message: str,
        warning_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize UnrealOn warning.
        
        Args:
            message: Human-readable warning message
            warning_code: Machine-readable warning code
            context: Additional context information
        """
        super().__init__(message)
        self.message = message
        self.warning_code = warning_code or self._get_default_warning_code()
        self.context = context or {}
        self.timestamp = utc_now()
    
    def _get_default_warning_code(self) -> str:
        """Get default warning code based on class name."""
        class_name = self.__class__.__name__
        import re
        warning_code = re.sub('([a-z0-9])([A-Z])', r'\1_\2', class_name).upper()
        return warning_code
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert warning to dictionary for serialization."""
        return {
            'warning_type': self.__class__.__name__,
            'warning_code': self.warning_code,
            'message': self.message,
            'context': self.context,
            'timestamp': self.timestamp.isoformat()
        }


class UnrealOnTimeoutError(UnrealOnError):
    """
    Base timeout error for operations that exceed time limits.
    
    Used when operations take longer than expected or configured
    timeout values are exceeded.
    """
    
    def __init__(
        self,
        message: str,
        timeout_seconds: Optional[float] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize timeout error.
        
        Args:
            message: Error message
            timeout_seconds: The timeout value that was exceeded
            operation: Name of the operation that timed out
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        
        if timeout_seconds is not None:
            self.add_context('timeout_seconds', timeout_seconds)
        
        if operation:
            self.add_context('operation', operation)


class UnrealOnConfigurationError(UnrealOnError):
    """
    Configuration-related errors.
    
    Used when there are issues with system configuration,
    invalid settings, or missing required configuration.
    """
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
        **kwargs
    ):
        """
        Initialize configuration error.
        
        Args:
            message: Error message
            config_key: The configuration key that caused the error
            config_value: The invalid configuration value
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        
        if config_key:
            self.add_context('config_key', config_key)
        
        if config_value is not None:
            self.add_context('config_value', str(config_value))


class UnrealOnRetryableError(UnrealOnError):
    """
    Base class for errors that can be retried.
    
    Used for temporary failures that might succeed
    if the operation is attempted again.
    """
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[float] = None,
        max_retries: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize retryable error.
        
        Args:
            message: Error message
            retry_after: Suggested delay before retry (seconds)
            max_retries: Maximum number of retries recommended
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        
        if retry_after is not None:
            self.add_context('retry_after', retry_after)
        
        if max_retries is not None:
            self.add_context('max_retries', max_retries)
    
    def should_retry(self, attempt_count: int) -> bool:
        """
        Check if the operation should be retried.
        
        Args:
            attempt_count: Number of attempts already made
            
        Returns:
            True if retry should be attempted
        """
        max_retries = self.context.get('max_retries')
        if max_retries is None:
            return True  # No limit specified
        
        return attempt_count < max_retries
    
    def get_retry_delay(self, attempt_count: int) -> float:
        """
        Get suggested delay before retry.
        
        Args:
            attempt_count: Number of attempts already made
            
        Returns:
            Delay in seconds
        """
        base_delay = self.context.get('retry_after', 1.0)
        
        # Exponential backoff: delay = base_delay * (2 ^ attempt_count)
        return base_delay * (2 ** min(attempt_count, 6))  # Cap at 2^6 = 64x


class UnrealOnFatalError(UnrealOnError):
    """
    Fatal errors that should stop system operation.
    
    Used for critical errors that indicate the system
    cannot continue operating safely.
    """
    
    def __init__(self, message: str, **kwargs):
        """Initialize fatal error."""
        super().__init__(message, **kwargs)
        self.add_context('fatal', True)
