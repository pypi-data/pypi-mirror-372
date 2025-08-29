"""
Health Check System

Comprehensive health monitoring for all system components.
Following critical requirements - max 500 lines, functions < 20 lines.

Phase 2: Core Systems - Monitoring
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict
from ..utils.time import utc_now

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class HealthCheckResult(BaseModel):
    """Result of a health check."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    component: str = Field(description="Component name")
    status: HealthStatus = Field(description="Health status")
    message: str = Field(description="Status message")
    timestamp: datetime = Field(description="Check timestamp")
    duration_ms: float = Field(description="Check duration in milliseconds")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details")
    
    def is_healthy(self) -> bool:
        """Check if component is healthy."""
        return self.status == HealthStatus.HEALTHY
    
    def is_degraded(self) -> bool:
        """Check if component is degraded."""
        return self.status == HealthStatus.DEGRADED


class ComponentHealth(BaseModel):
    """Health information for a component."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    name: str = Field(description="Component name")
    current_status: HealthStatus = Field(description="Current health status")
    last_check: datetime = Field(description="Last health check time")
    check_count: int = Field(default=0, description="Total health checks performed")
    failure_count: int = Field(default=0, description="Number of failed checks")
    last_failure: Optional[datetime] = Field(default=None, description="Last failure time")
    uptime_start: datetime = Field(description="When component became healthy")
    
    def get_uptime_seconds(self) -> float:
        """Get uptime in seconds."""
        if self.current_status != HealthStatus.HEALTHY:
            return 0.0
        return (utc_now() - self.uptime_start).total_seconds()
    
    def get_failure_rate(self) -> float:
        """Get failure rate as percentage."""
        if self.check_count == 0:
            return 0.0
        return (self.failure_count / self.check_count) * 100.0


class HealthChecker:
    """
    Health checker for system components.
    
    Provides centralized health monitoring with configurable
    check intervals and failure thresholds.
    """
    
    def __init__(self, check_interval: float = 30.0):
        """Initialize health checker."""
        self.check_interval = check_interval
        self._components: Dict[str, ComponentHealth] = {}
        self._check_functions: Dict[str, Callable] = {}
        self._running = False
        self._check_task: Optional[asyncio.Task] = None
        self.logger = logging.getLogger("health_checker")
    
    def register_component(
        self, 
        name: str, 
        check_func: Callable[[], Any]
    ) -> None:
        """
        Register component for health monitoring.
        
        Args:
            name: Component name
            check_func: Async function that returns health status
        """
        self._check_functions[name] = check_func
        self._components[name] = ComponentHealth(
            name=name,
            current_status=HealthStatus.UNKNOWN,
            last_check=utc_now(),
            uptime_start=utc_now()
        )
        
        self.logger.info(f"Registered health check for component: {name}")
    
    async def check_component(self, name: str) -> HealthCheckResult:
        """
        Perform health check for specific component.
        
        Args:
            name: Component name
            
        Returns:
            HealthCheckResult with check outcome
        """
        if name not in self._check_functions:
            return HealthCheckResult(
                component=name,
                status=HealthStatus.UNKNOWN,
                message="Component not registered",
                timestamp=utc_now(),
                duration_ms=0.0
            )
        
        start_time = utc_now()
        
        try:
            check_func = self._check_functions[name]
            
            # Execute health check with timeout
            result = await asyncio.wait_for(check_func(), timeout=10.0)
            
            duration = (utc_now() - start_time).total_seconds() * 1000
            
            # Determine status from result
            if isinstance(result, bool):
                status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                message = "Health check passed" if result else "Health check failed"
                details = {}
            elif isinstance(result, dict):
                status = HealthStatus(result.get('status', 'unknown'))
                message = result.get('message', 'No message')
                details = result.get('details', {})
            else:
                status = HealthStatus.HEALTHY
                message = str(result)
                details = {}
            
            # Update component health
            await self._update_component_health(name, status)
            
            return HealthCheckResult(
                component=name,
                status=status,
                message=message,
                timestamp=utc_now(),
                duration_ms=duration,
                details=details
            )
            
        except asyncio.TimeoutError:
            duration = (utc_now() - start_time).total_seconds() * 1000
            await self._update_component_health(name, HealthStatus.UNHEALTHY)
            
            return HealthCheckResult(
                component=name,
                status=HealthStatus.UNHEALTHY,
                message="Health check timed out",
                timestamp=utc_now(),
                duration_ms=duration
            )
            
        except Exception as e:
            duration = (utc_now() - start_time).total_seconds() * 1000
            await self._update_component_health(name, HealthStatus.UNHEALTHY)
            
            return HealthCheckResult(
                component=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check error: {str(e)}",
                timestamp=utc_now(),
                duration_ms=duration
            )
    
    async def check_all_components(self) -> List[HealthCheckResult]:
        """Check health of all registered components."""
        results = []
        
        for name in self._check_functions.keys():
            result = await self.check_component(name)
            results.append(result)
        
        return results
    
    async def _update_component_health(
        self, 
        name: str, 
        status: HealthStatus
    ) -> None:
        """Update component health tracking."""
        if name not in self._components:
            return
        
        component = self._components[name]
        component.last_check = utc_now()
        component.check_count += 1
        
        # Track status changes
        if status != component.current_status:
            if status == HealthStatus.HEALTHY:
                component.uptime_start = utc_now()
                self.logger.info(f"Component {name} became healthy")
            else:
                self.logger.warning(f"Component {name} status changed to {status}")
        
        # Track failures
        if status in [HealthStatus.UNHEALTHY, HealthStatus.DEGRADED]:
            component.failure_count += 1
            component.last_failure = utc_now()
        
        component.current_status = status
    
    async def start_monitoring(self) -> None:
        """Start continuous health monitoring."""
        if self._running:
            self.logger.warning("Health monitoring already running")
            return
        
        self._running = True
        self._check_task = asyncio.create_task(self._monitoring_loop())
        
        self.logger.info(f"Started health monitoring (interval: {self.check_interval}s)")
    
    async def stop_monitoring(self) -> None:
        """Stop health monitoring."""
        self._running = False
        
        if self._check_task and not self._check_task.done():
            self._check_task.cancel()
            try:
                await self._check_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Stopped health monitoring")
    
    async def _monitoring_loop(self) -> None:
        """Background monitoring loop."""
        try:
            while self._running:
                await self.check_all_components()
                await asyncio.sleep(self.check_interval)
                
        except asyncio.CancelledError:
            self.logger.debug("Monitoring loop cancelled")
            raise
        except Exception as e:
            self.logger.error(f"Error in monitoring loop: {e}")
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health summary."""
        if not self._components:
            return {
                'overall_status': HealthStatus.UNKNOWN,
                'components': {},
                'summary': {
                    'total': 0,
                    'healthy': 0,
                    'degraded': 0,
                    'unhealthy': 0,
                    'unknown': 0
                }
            }
        
        # Count component statuses
        status_counts = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.DEGRADED: 0,
            HealthStatus.UNHEALTHY: 0,
            HealthStatus.UNKNOWN: 0
        }
        
        components_data = {}
        
        for name, component in self._components.items():
            status_counts[component.current_status] += 1
            components_data[name] = {
                'status': component.current_status,
                'last_check': component.last_check.isoformat(),
                'uptime_seconds': component.get_uptime_seconds(),
                'failure_rate': component.get_failure_rate(),
                'check_count': component.check_count
            }
        
        # Determine overall status
        if status_counts[HealthStatus.UNHEALTHY] > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif status_counts[HealthStatus.DEGRADED] > 0:
            overall_status = HealthStatus.DEGRADED
        elif status_counts[HealthStatus.HEALTHY] == len(self._components):
            overall_status = HealthStatus.HEALTHY
        else:
            overall_status = HealthStatus.UNKNOWN
        
        return {
            'overall_status': overall_status,
            'components': components_data,
            'summary': {
                'total': len(self._components),
                'healthy': status_counts[HealthStatus.HEALTHY],
                'degraded': status_counts[HealthStatus.DEGRADED],
                'unhealthy': status_counts[HealthStatus.UNHEALTHY],
                'unknown': status_counts[HealthStatus.UNKNOWN]
            }
        }


# Global health checker instance
_global_health_checker = HealthChecker()


def get_health_checker() -> HealthChecker:
    """Get global health checker instance."""
    return _global_health_checker


def health_check_decorator(component_name: str):
    """
    Decorator to register function as health check.
    
    Args:
        component_name: Name of component to monitor
    """
    def decorator(func: Callable) -> Callable:
        _global_health_checker.register_component(component_name, func)
        return func
    
    return decorator
