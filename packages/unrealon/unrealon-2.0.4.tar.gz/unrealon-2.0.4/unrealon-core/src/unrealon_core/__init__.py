"""
UnrealOn Core Package

Core models, enums, and exceptions for the UnrealOn RPC system.
This package provides the foundational data structures and utilities
used across all UnrealOn components.

Phase 1: Bedrock Foundation
- Base Pydantic models with strict validation
- Core enums and constants
- Custom exceptions hierarchy
- 100% test coverage required
"""

# Import unified version system
from unrealon_core.version import get_rpc_version, get_version_info

__version__ = get_rpc_version()
__author__ = "UnrealOn Team"

# Import main components for easy access
from .models.base import UnrealOnBaseModel, TimestampedModel, IdentifiedModel, StatusModel
from .models.arq_context import (
    ARQWorkerContext, ARQWorkerStats, TaskAssignmentParams, TaskResultParams,
    LogEntryParams, DriverRegistrationParams, HeartbeatParams
)
from .models.arq_responses import (
    TaskAssignmentResponse, TaskResultResponse, LogEntryResponse,
    DriverRegistrationResponse, HeartbeatResponse, PingResponse
)
from .models.typed_responses import (
    HealthCheckResult, StatusInfo, SessionInfo, ProxyStats,
    ThreadStats, CacheStats, BatchStats
)
from .models.communication import (
    MessageType as WebSocketMessageType, WebSocketMessage, 
    DriverRegistrationMessage, RegistrationResponseMessage,
    TaskAssignmentMessage, TaskResultMessage,
    LogEntryMessage, LogBatchMessage,
    HeartbeatMessage, ConfigurationUpdateMessage,
    ErrorMessage, AckMessage,
    create_error_message, create_ack_message,
    # Data models for strict typing
    TaskAssignmentData, TaskResultData,
    DriverRegistrationData, HeartbeatData, LogEntryData, LogContext
)
from .enums.status import DriverStatus, TaskStatus, ProxyStatus, LogLevel
from .enums.types import MessageType, ProxyType, TaskPriority
from .exceptions.base import UnrealOnError
from .exceptions.validation import ValidationError as UnrealOnValidationError
from .exceptions.communication import CommunicationError

# Error handling system
from .error_handling import (
    RetryConfig, RetryStrategy, RetryResult,
    ExponentialBackoff, LinearBackoff, FixedBackoff,
    retry_async, retry_sync,
    CircuitBreakerConfig, CircuitBreakerState,
    CircuitBreaker, circuit_breaker,
    ErrorContext, ErrorSeverity,
    create_error_context, format_error_context,
    RecoveryStrategy, RecoveryAction,
    AutoRecovery, recovery_handler
)

# Monitoring system
from .monitoring import (
    HealthStatus, HealthCheckResult, ComponentHealth,
    HealthChecker, health_check_decorator,
    MetricType, MetricValue, Metric,
    MetricsCollector, counter, gauge, histogram, timer,
    AlertSeverity, AlertRule, Alert,
    AlertManager, alert_on_condition,
    DashboardData, SystemStatus,
    MonitoringDashboard, get_system_overview
)

# Configuration system
from .config import (
    EnvironmentConfig, URLConfig,
    get_environment_config, get_url_config
)

__all__ = [
    # Version info
    "__version__",
    "__author__", 
    "__phase__",
    
    # Base models
    "UnrealOnBaseModel",
    "TimestampedModel", 
    "IdentifiedModel",
    "StatusModel",
    
    # WebSocket Communication models
    "WebSocketMessageType",
    "WebSocketMessage",
    "DriverRegistrationMessage",
    "RegistrationResponseMessage", 
    "TaskAssignmentMessage",
    "TaskResultMessage",
    "LogEntryMessage",
    "LogBatchMessage",
    "HeartbeatMessage",
    "ConfigurationUpdateMessage",
    "ErrorMessage",
    "AckMessage",
    "create_error_message",
    "create_ack_message",
    
    # Data models for strict typing
    "TaskAssignmentData",
    "TaskResultData", 
    "DriverRegistrationData",
    "HeartbeatData",
    "LogEntryData",
    "LogContext",
    
    # Status enums
    "DriverStatus",
    "TaskStatus",
    "ProxyStatus", 
    "LogLevel",
    
    # Type enums
    "MessageType",
    "ProxyType",
    "TaskPriority",
    
    # Exceptions
    "UnrealOnError",
    "UnrealOnValidationError",
    "CommunicationError",
    
    # Error handling system
    "RetryConfig", "RetryStrategy", "RetryResult",
    "ExponentialBackoff", "LinearBackoff", "FixedBackoff",
    "retry_async", "retry_sync",
    "CircuitBreakerConfig", "CircuitBreakerState",
    "CircuitBreaker", "circuit_breaker",
    "ErrorContext", "ErrorSeverity",
    "create_error_context", "format_error_context",
    "RecoveryStrategy", "RecoveryAction",
    "AutoRecovery", "recovery_handler",
    
    # Monitoring system
    "HealthStatus", "HealthCheckResult", "ComponentHealth",
    "HealthChecker", "health_check_decorator",
    "MetricType", "MetricValue", "Metric",
    "MetricsCollector", "counter", "gauge", "histogram", "timer",
    "AlertSeverity", "AlertRule", "Alert",
    "AlertManager", "alert_on_condition",
    "DashboardData", "SystemStatus",
    "MonitoringDashboard", "get_system_overview",
    
    # Configuration system
    "EnvironmentConfig", "URLConfig",
    "get_environment_config", "get_url_config",
]
