"""
Typed Response Models

Strictly typed models to replace Dict[str, Any] usage.
Following critical requirements - no raw Dict[str, Any].

Phase 2: Core Systems - Typed Responses
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from .base import UnrealOnBaseModel


class HealthCheckDetails(UnrealOnBaseModel):
    """Health check details model."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    manager_status: str = Field(description="Manager status")
    success_rate: float = Field(description="Success rate percentage")
    total_operations: int = Field(description="Total operations count")
    uptime_seconds: float = Field(description="Uptime in seconds")


class HealthCheckResult(UnrealOnBaseModel):
    """Health check result model."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    status: str = Field(description="Health status")
    message: str = Field(description="Health message")
    details: HealthCheckDetails = Field(description="Health details")


class StatusInfo(UnrealOnBaseModel):
    """Status information model."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    name: str = Field(description="Component name")
    status: str = Field(description="Component status")
    enabled: bool = Field(description="Whether component is enabled")
    uptime_seconds: Optional[float] = Field(default=None, description="Uptime in seconds")
    initialization_time: Optional[str] = Field(default=None, description="Initialization time ISO string")
    shutdown_time: Optional[str] = Field(default=None, description="Shutdown time ISO string")
    stats: "StatsModel" = Field(description="Component statistics")
    config: "ConfigModel" = Field(description="Component configuration")


class StatsModel(UnrealOnBaseModel):
    """Statistics model."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    operations_total: int = Field(default=0, description="Total operations")
    operations_successful: int = Field(default=0, description="Successful operations")
    operations_failed: int = Field(default=0, description="Failed operations")
    last_operation_time: Optional[str] = Field(default=None, description="Last operation time ISO string")
    average_operation_time: float = Field(default=0.0, description="Average operation time")


class ConfigModel(UnrealOnBaseModel):
    """Configuration model."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    enabled: bool = Field(description="Whether enabled")
    timeout_seconds: float = Field(description="Timeout in seconds")
    retry_count: int = Field(description="Retry count")
    log_level: str = Field(description="Log level")


class SessionInfo(UnrealOnBaseModel):
    """HTTP session information model."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    cookies_count: int = Field(description="Number of cookies")
    has_proxy_manager: bool = Field(description="Whether proxy manager is available")
    use_proxy_manager: bool = Field(description="Whether using proxy manager")
    max_connections: int = Field(description="Maximum connections")
    default_timeout: float = Field(description="Default timeout")


class ProxyStats(UnrealOnBaseModel):
    """Proxy statistics model."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    total_proxies: int = Field(description="Total proxies")
    healthy_proxies: int = Field(description="Healthy proxies")
    banned_proxies: int = Field(description="Banned proxies")
    average_success_rate: float = Field(description="Average success rate")
    rotation_strategy: str = Field(description="Rotation strategy")
    current_index: int = Field(description="Current rotation index")
    has_rpc_client: bool = Field(description="Whether RPC client is available")


class ThreadStats(UnrealOnBaseModel):
    """Thread statistics model."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    thread_pools: "ThreadPoolsInfo" = Field(description="Thread pools information")
    concurrency: "ConcurrencyInfo" = Field(description="Concurrency information")
    active_task_names: List[str] = Field(description="Active task names")


class ThreadPoolsInfo(UnrealOnBaseModel):
    """Thread pools information model."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    io_bound: "ThreadPoolInfo" = Field(description="I/O bound thread pool")
    cpu_bound: "ThreadPoolInfo" = Field(description="CPU bound thread pool")
    general: "ThreadPoolInfo" = Field(description="General thread pool")


class ThreadPoolInfo(UnrealOnBaseModel):
    """Thread pool information model."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    max_workers: int = Field(description="Maximum workers")
    available: bool = Field(description="Whether available")


class ConcurrencyInfo(UnrealOnBaseModel):
    """Concurrency information model."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    max_concurrent_tasks: int = Field(description="Maximum concurrent tasks")
    active_tasks: int = Field(description="Active tasks")
    semaphore_available: int = Field(description="Available semaphore permits")


class CacheStats(UnrealOnBaseModel):
    """Cache statistics model."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    entries: int = Field(description="Number of entries")
    max_entries: int = Field(description="Maximum entries")
    memory_usage_mb: float = Field(description="Memory usage in MB")
    max_memory_mb: int = Field(description="Maximum memory in MB")
    hits: int = Field(description="Cache hits")
    misses: int = Field(description="Cache misses")
    hit_rate_percent: float = Field(description="Hit rate percentage")
    evictions: int = Field(description="Number of evictions")
    eviction_strategy: str = Field(description="Eviction strategy")


class BatchStats(UnrealOnBaseModel):
    """Batch statistics model."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    current_batch_size: int = Field(description="Current batch size")
    max_batch_size: int = Field(description="Maximum batch size")
    batch_timeout: float = Field(description="Batch timeout")
    has_rpc_client: bool = Field(description="Whether RPC client is available")


# Update forward references
StatusInfo.model_rebuild()
ThreadStats.model_rebuild()
ThreadPoolsInfo.model_rebuild()
