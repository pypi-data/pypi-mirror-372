"""
Status enums for UnrealOn system.

These enums define all possible status values for different
components in the system. Using enums ensures type safety
and prevents invalid status values.

Phase 1: Foundation status enums
"""

from enum import Enum


class DriverStatus(str, Enum):
    """
    Driver connection and operational status.
    
    Used to track the current state of driver connections
    and their ability to process tasks.
    """
    
    # Connection states
    DISCONNECTED = "disconnected"    # Driver is not connected
    CONNECTING = "connecting"        # Driver is attempting to connect
    CONNECTED = "connected"          # Driver is connected and idle
    
    # Operational states  
    BUSY = "busy"                   # Driver is processing a task
    READY = "ready"                 # Driver is ready to receive tasks
    
    # Error states
    ERROR = "error"                 # Driver encountered an error
    TIMEOUT = "timeout"             # Driver connection timed out
    
    # Maintenance states
    MAINTENANCE = "maintenance"     # Driver is in maintenance mode
    SHUTDOWN = "shutdown"           # Driver is shutting down
    
    def is_connected(self) -> bool:
        """Check if driver is in a connected state."""
        return self in [
            DriverStatus.CONNECTED,
            DriverStatus.BUSY, 
            DriverStatus.READY
        ]
    
    def is_available(self) -> bool:
        """Check if driver is available for new tasks."""
        return self in [
            DriverStatus.CONNECTED,
            DriverStatus.READY
        ]
    
    def is_error_state(self) -> bool:
        """Check if driver is in an error state."""
        return self in [
            DriverStatus.ERROR,
            DriverStatus.TIMEOUT
        ]


class TaskStatus(str, Enum):
    """
    Task execution status throughout its lifecycle.
    
    Tracks a task from creation through completion,
    including error and retry states.
    """
    
    # Initial states
    CREATED = "created"             # Task created but not queued
    PENDING = "pending"             # Task queued, waiting for assignment
    ASSIGNED = "assigned"           # Task assigned to a driver
    
    # Execution states
    RUNNING = "running"             # Task is being executed
    PAUSED = "paused"              # Task execution paused
    
    # Completion states
    COMPLETED = "completed"         # Task completed successfully
    FAILED = "failed"              # Task failed permanently
    CANCELLED = "cancelled"        # Task was cancelled
    
    # Retry states
    RETRYING = "retrying"          # Task is being retried
    RETRY_FAILED = "retry_failed"  # All retries exhausted
    
    # Timeout states
    TIMEOUT = "timeout"            # Task execution timed out
    
    def is_active(self) -> bool:
        """Check if task is actively being processed."""
        return self in [
            TaskStatus.ASSIGNED,
            TaskStatus.RUNNING,
            TaskStatus.RETRYING
        ]
    
    def is_completed(self) -> bool:
        """Check if task has reached a final state."""
        return self in [
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
            TaskStatus.RETRY_FAILED,
            TaskStatus.TIMEOUT
        ]
    
    def is_successful(self) -> bool:
        """Check if task completed successfully."""
        return self == TaskStatus.COMPLETED
    
    def can_retry(self) -> bool:
        """Check if task can be retried."""
        return self in [
            TaskStatus.FAILED,
            TaskStatus.TIMEOUT
        ]


class ProxyStatus(str, Enum):
    """
    Proxy server health and availability status.
    
    Used to track proxy server health and determine
    which proxies should be used for requests.
    """
    
    # Operational states
    ACTIVE = "active"              # Proxy is healthy and available
    INACTIVE = "inactive"          # Proxy is temporarily unavailable
    
    # Health states
    HEALTHY = "healthy"            # Proxy is responding normally
    DEGRADED = "degraded"          # Proxy is slow but functional
    
    # Error states
    BANNED = "banned"              # Proxy is banned/blocked
    TIMEOUT = "timeout"            # Proxy is not responding
    ERROR = "error"                # Proxy returned errors
    
    # Testing states
    TESTING = "testing"            # Proxy is being health-checked
    UNKNOWN = "unknown"            # Proxy status is unknown
    
    def is_usable(self) -> bool:
        """Check if proxy can be used for requests."""
        return self in [
            ProxyStatus.ACTIVE,
            ProxyStatus.HEALTHY,
            ProxyStatus.DEGRADED
        ]
    
    def is_healthy(self) -> bool:
        """Check if proxy is in good health."""
        return self in [
            ProxyStatus.ACTIVE,
            ProxyStatus.HEALTHY
        ]
    
    def needs_health_check(self) -> bool:
        """Check if proxy needs a health check."""
        return self in [
            ProxyStatus.UNKNOWN,
            ProxyStatus.TIMEOUT,
            ProxyStatus.ERROR
        ]


class LogLevel(str, Enum):
    """
    Logging levels for the UnrealOn system.
    
    Standard logging levels with additional
    system-specific levels for better categorization.
    """
    
    # Standard levels
    DEBUG = "debug"                # Detailed debugging information
    INFO = "info"                  # General information
    WARNING = "warning"            # Warning messages
    ERROR = "error"                # Error messages
    CRITICAL = "critical"          # Critical system errors
    
    # System-specific levels
    TRACE = "trace"                # Very detailed tracing
    PERFORMANCE = "performance"    # Performance-related logs
    SECURITY = "security"          # Security-related logs
    AUDIT = "audit"               # Audit trail logs
    
    def get_numeric_level(self) -> int:
        """Get numeric level for comparison."""
        levels = {
            LogLevel.TRACE: 5,
            LogLevel.DEBUG: 10,
            LogLevel.INFO: 20,
            LogLevel.PERFORMANCE: 25,
            LogLevel.WARNING: 30,
            LogLevel.ERROR: 40,
            LogLevel.SECURITY: 45,
            LogLevel.CRITICAL: 50,
            LogLevel.AUDIT: 60,
        }
        return levels.get(self, 20)
    
    def is_at_least(self, other: 'LogLevel') -> bool:
        """Check if this level is at least as severe as another."""
        return self.get_numeric_level() >= other.get_numeric_level()
    
    @classmethod
    def from_string(cls, level_str: str) -> 'LogLevel':
        """Create LogLevel from string, with fallback to INFO."""
        try:
            return cls(level_str.lower())
        except ValueError:
            return cls.INFO
