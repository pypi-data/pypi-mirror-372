"""
Circuit Breaker Pattern

Prevents cascading failures by temporarily disabling failing services.
Following critical requirements - max 500 lines, functions < 20 lines.

Phase 2: Core Systems - Error Handling
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Optional, Dict
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict

from ..exceptions.base import UnrealOnError
from ..utils.time import utc_now

logger = logging.getLogger(__name__)


class CircuitBreakerState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, requests blocked
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerError(UnrealOnError):
    """Circuit breaker is open."""
    pass


class CircuitBreakerConfig(BaseModel):
    """Configuration for circuit breaker."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    failure_threshold: int = Field(
        default=5, 
        ge=1, 
        le=20, 
        description="Failures needed to open circuit"
    )
    recovery_timeout: float = Field(
        default=60.0, 
        ge=1.0, 
        le=300.0, 
        description="Seconds before trying half-open"
    )
    success_threshold: int = Field(
        default=3, 
        ge=1, 
        le=10, 
        description="Successes needed to close circuit"
    )
    timeout: float = Field(
        default=30.0, 
        ge=1.0, 
        le=120.0, 
        description="Operation timeout in seconds"
    )


class CircuitBreakerStats(BaseModel):
    """Circuit breaker statistics."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    total_requests: int = Field(default=0, description="Total requests processed")
    successful_requests: int = Field(default=0, description="Successful requests")
    failed_requests: int = Field(default=0, description="Failed requests")
    rejected_requests: int = Field(default=0, description="Requests rejected by circuit")
    last_failure_time: Optional[datetime] = Field(default=None, description="Last failure timestamp")
    last_success_time: Optional[datetime] = Field(default=None, description="Last success timestamp")
    
    def get_failure_rate(self) -> float:
        """Calculate failure rate percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.failed_requests / self.total_requests) * 100.0


class CircuitBreaker:
    """
    Circuit breaker implementation.
    
    Prevents cascading failures by monitoring service health
    and temporarily blocking requests to failing services.
    """
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        """Initialize circuit breaker."""
        self.name = name
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.stats = CircuitBreakerStats()
        
        # State tracking
        self._consecutive_failures = 0
        self._consecutive_successes = 0
        self._last_failure_time: Optional[datetime] = None
        self._lock = asyncio.Lock()
        
        self.logger = logging.getLogger(f"circuit_breaker.{name}")
    
    async def call(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.
        
        Args:
            func: Function to execute
            *args, **kwargs: Function arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerError: If circuit is open
        """
        async with self._lock:
            await self._update_state()
            
            if self.state == CircuitBreakerState.OPEN:
                self.stats.rejected_requests += 1
                self.logger.warning(f"Circuit breaker {self.name} is OPEN - rejecting request")
                raise CircuitBreakerError(f"Circuit breaker {self.name} is open")
            
            self.stats.total_requests += 1
        
        # Execute function with timeout
        try:
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=self.config.timeout
            )
            
            await self._record_success()
            return result
            
        except Exception as e:
            await self._record_failure()
            raise
    
    async def _update_state(self) -> None:
        """Update circuit breaker state based on current conditions."""
        now = utc_now()
        
        if self.state == CircuitBreakerState.OPEN:
            # Check if we should transition to half-open
            if (self._last_failure_time and 
                (now - self._last_failure_time).total_seconds() >= self.config.recovery_timeout):
                
                self.state = CircuitBreakerState.HALF_OPEN
                self._consecutive_successes = 0
                self.logger.info(f"Circuit breaker {self.name} transitioning to HALF_OPEN")
        
        elif self.state == CircuitBreakerState.HALF_OPEN:
            # Check if we should close the circuit
            if self._consecutive_successes >= self.config.success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self._consecutive_failures = 0
                self.logger.info(f"Circuit breaker {self.name} transitioning to CLOSED")
    
    async def _record_success(self) -> None:
        """Record successful operation."""
        async with self._lock:
            self.stats.successful_requests += 1
            self.stats.last_success_time = utc_now()
            
            if self.state == CircuitBreakerState.HALF_OPEN:
                self._consecutive_successes += 1
                self.logger.debug(
                    f"Circuit breaker {self.name} success "
                    f"({self._consecutive_successes}/{self.config.success_threshold})"
                )
            
            # Reset failure counter on success
            self._consecutive_failures = 0
    
    async def _record_failure(self) -> None:
        """Record failed operation."""
        async with self._lock:
            self.stats.failed_requests += 1
            self.stats.last_failure_time = utc_now()
            self._last_failure_time = self.stats.last_failure_time
            
            self._consecutive_failures += 1
            self._consecutive_successes = 0
            
            self.logger.debug(
                f"Circuit breaker {self.name} failure "
                f"({self._consecutive_failures}/{self.config.failure_threshold})"
            )
            
            # Check if we should open the circuit
            if (self.state == CircuitBreakerState.CLOSED and 
                self._consecutive_failures >= self.config.failure_threshold):
                
                self.state = CircuitBreakerState.OPEN
                self.logger.warning(f"Circuit breaker {self.name} transitioning to OPEN")
            
            elif self.state == CircuitBreakerState.HALF_OPEN:
                # Any failure in half-open state reopens the circuit
                self.state = CircuitBreakerState.OPEN
                self.logger.warning(f"Circuit breaker {self.name} reopening due to failure in HALF_OPEN")
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status."""
        return {
            'name': self.name,
            'state': self.state.value,
            'consecutive_failures': self._consecutive_failures,
            'consecutive_successes': self._consecutive_successes,
            'config': self.config.model_dump(),
            'stats': self.stats.model_dump()
        }
    
    def reset(self) -> None:
        """Reset circuit breaker to closed state."""
        self.state = CircuitBreakerState.CLOSED
        self._consecutive_failures = 0
        self._consecutive_successes = 0
        self._last_failure_time = None
        self.logger.info(f"Circuit breaker {self.name} manually reset to CLOSED")


# Global circuit breaker registry
_circuit_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(
    name: str, 
    config: Optional[CircuitBreakerConfig] = None
) -> CircuitBreaker:
    """Get or create circuit breaker by name."""
    if name not in _circuit_breakers:
        if config is None:
            config = CircuitBreakerConfig()
        _circuit_breakers[name] = CircuitBreaker(name, config)
    
    return _circuit_breakers[name]


def circuit_breaker(
    name: str, 
    config: Optional[CircuitBreakerConfig] = None
):
    """Decorator to wrap function with circuit breaker."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        cb = get_circuit_breaker(name, config)
        
        async def async_wrapper(*args, **kwargs):
            return await cb.call(func, *args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            # For sync functions, we need to handle differently
            # This is a simplified version - in production you might want
            # to use threading or a different approach
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(cb.call(func, *args, **kwargs))
            except RuntimeError:
                # No event loop running
                return asyncio.run(cb.call(func, *args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def get_all_circuit_breakers() -> Dict[str, Dict[str, Any]]:
    """Get status of all circuit breakers."""
    return {name: cb.get_status() for name, cb in _circuit_breakers.items()}


def reset_all_circuit_breakers() -> None:
    """Reset all circuit breakers."""
    for cb in _circuit_breakers.values():
        cb.reset()
