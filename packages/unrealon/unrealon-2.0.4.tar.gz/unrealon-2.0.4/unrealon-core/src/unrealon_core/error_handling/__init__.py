"""
Error Handling Package

Comprehensive error handling and retry logic for UnrealOn RPC system.
Following critical requirements - max 500 lines, 100% Pydantic v2.

Phase 2: Core Systems - Error Handling
"""

from .retry import (
    RetryConfig, RetryStrategy, RetryResult,
    ExponentialBackoff, LinearBackoff, FixedBackoff,
    retry_async, retry_sync
)
from .circuit_breaker import (
    CircuitBreakerConfig, CircuitBreakerState,
    CircuitBreaker, circuit_breaker, get_circuit_breaker
)
from .error_context import (
    ErrorContext, ErrorSeverity,
    create_error_context, format_error_context
)
from .recovery import (
    RecoveryStrategy, RecoveryAction,
    AutoRecovery, recovery_handler
)

__all__ = [
    # Retry system
    'RetryConfig', 'RetryStrategy', 'RetryResult',
    'ExponentialBackoff', 'LinearBackoff', 'FixedBackoff',
    'retry_async', 'retry_sync',
    
    # Circuit breaker
    'CircuitBreakerConfig', 'CircuitBreakerState',
    'CircuitBreaker', 'circuit_breaker', 'get_circuit_breaker',
    
    # Error context
    'ErrorContext', 'ErrorSeverity',
    'create_error_context', 'format_error_context',
    
    # Recovery system
    'RecoveryStrategy', 'RecoveryAction',
    'AutoRecovery', 'recovery_handler',
]
