"""
Clean protocols for module system.
"""

from abc import abstractmethod
from typing import Protocol, Dict, Any, Optional
from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class ModuleStatus(str, Enum):
    """Module lifecycle status."""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    INITIALIZED = "initialized"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class EventType(str, Enum):
    """Event types for module communication."""
    MODULE_INITIALIZED = "module_initialized"
    MODULE_STARTED = "module_started"
    MODULE_STOPPED = "module_stopped"
    MODULE_ERROR = "module_error"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    HEALTH_CHECK = "health_check"


class HealthStatus(str, Enum):
    """Health check status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ModuleEvent(BaseModel):
    """Event data structure."""
    event_type: EventType
    module_name: str
    timestamp: datetime
    data: Dict[str, Any] = {}
    error: Optional[str] = None
    
    model_config = {"extra": "forbid"}


class HealthCheckResult(BaseModel):
    """Health check result."""
    status: HealthStatus
    timestamp: datetime
    details: Dict[str, Any] = {}
    error: Optional[str] = None
    response_time_ms: Optional[float] = None
    
    model_config = {"extra": "forbid"}


class BaseModule(Protocol):
    """Base module protocol."""
    
    @property
    def name(self) -> str:
        """Module name."""
        ...
    
    @property
    def status(self) -> ModuleStatus:
        """Current module status."""
        ...
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize module."""
        ...
    
    @abstractmethod
    async def start(self) -> bool:
        """Start module."""
        ...
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop module."""
        ...
    
    @abstractmethod
    async def health_check(self) -> HealthCheckResult:
        """Perform health check."""
        ...
