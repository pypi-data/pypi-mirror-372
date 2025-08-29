"""
Recovery System

Automatic error recovery and healing mechanisms.
Following critical requirements - max 500 lines, functions < 20 lines.

Phase 2: Core Systems - Error Handling
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict

from .error_context import ErrorContext, ErrorSeverity
from ..utils.time import utc_now


logger = logging.getLogger(__name__)


class RecoveryStrategy(str, Enum):
    """Recovery strategy types."""
    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAK = "circuit_break"
    GRACEFUL_DEGRADE = "graceful_degrade"
    RESTART = "restart"


class RecoveryAction(BaseModel):
    """Recovery action configuration."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    strategy: RecoveryStrategy = Field(description="Recovery strategy to use")
    max_attempts: int = Field(default=3, ge=1, le=10, description="Maximum recovery attempts")
    delay_seconds: float = Field(default=1.0, ge=0.1, le=60.0, description="Delay between attempts")
    timeout_seconds: float = Field(default=30.0, ge=1.0, le=300.0, description="Recovery timeout")
    fallback_value: Optional[Any] = Field(default=None, description="Fallback value to return")
    enabled: bool = Field(default=True, description="Whether recovery is enabled")


class RecoveryResult(BaseModel):
    """Result of recovery attempt."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    success: bool = Field(description="Whether recovery succeeded")
    strategy_used: RecoveryStrategy = Field(description="Strategy that was used")
    attempts_made: int = Field(description="Number of recovery attempts")
    duration_seconds: float = Field(description="Total recovery duration")
    result: Optional[Any] = Field(default=None, description="Recovery result")
    error_message: Optional[str] = Field(default=None, description="Error if recovery failed")


class AutoRecovery:
    """
    Automatic recovery system.
    
    Provides intelligent error recovery based on error context
    and configured recovery strategies.
    """
    
    def __init__(self):
        """Initialize auto recovery system."""
        self._recovery_actions: Dict[str, RecoveryAction] = {}
        self._recovery_stats: Dict[str, Dict[str, int]] = {}
        self.logger = logging.getLogger("auto_recovery")
    
    def register_recovery_action(
        self, 
        error_type: str, 
        action: RecoveryAction
    ) -> None:
        """
        Register recovery action for error type.
        
        Args:
            error_type: Exception class name
            action: Recovery action configuration
        """
        self._recovery_actions[error_type] = action
        self._recovery_stats[error_type] = {
            'attempts': 0,
            'successes': 0,
            'failures': 0
        }
        
        self.logger.info(f"Registered recovery action for {error_type}: {action.strategy}")
    
    async def attempt_recovery(
        self,
        error_context: ErrorContext,
        operation_func: Callable[..., Any],
        *args,
        **kwargs
    ) -> RecoveryResult:
        """
        Attempt to recover from error.
        
        Args:
            error_context: Context of the error
            operation_func: Function to retry
            *args, **kwargs: Function arguments
            
        Returns:
            RecoveryResult with outcome
        """
        start_time = utc_now()
        error_type = error_context.error_type
        
        # Get recovery action for this error type
        action = self._recovery_actions.get(error_type)
        if not action or not action.enabled:
            self.logger.debug(f"No recovery action configured for {error_type}")
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.RETRY,
                attempts_made=0,
                duration_seconds=0.0,
                error_message="No recovery action configured"
            )
        
        # Update stats
        self._recovery_stats[error_type]['attempts'] += 1
        
        # Attempt recovery based on strategy
        try:
            if action.strategy == RecoveryStrategy.RETRY:
                result = await self._retry_recovery(action, operation_func, *args, **kwargs)
            elif action.strategy == RecoveryStrategy.FALLBACK:
                result = await self._fallback_recovery(action, operation_func, *args, **kwargs)
            elif action.strategy == RecoveryStrategy.GRACEFUL_DEGRADE:
                result = await self._graceful_degrade_recovery(action, operation_func, *args, **kwargs)
            else:
                result = RecoveryResult(
                    success=False,
                    strategy_used=action.strategy,
                    attempts_made=0,
                    duration_seconds=0.0,
                    error_message=f"Recovery strategy {action.strategy} not implemented"
                )
            
            # Update stats
            if result.success:
                self._recovery_stats[error_type]['successes'] += 1
            else:
                self._recovery_stats[error_type]['failures'] += 1
            
            # Calculate duration
            duration = (utc_now() - start_time).total_seconds()
            result.duration_seconds = duration
            
            return result
            
        except Exception as e:
            self.logger.error(f"Recovery attempt failed: {e}")
            self._recovery_stats[error_type]['failures'] += 1
            
            duration = (utc_now() - start_time).total_seconds()
            return RecoveryResult(
                success=False,
                strategy_used=action.strategy,
                attempts_made=1,
                duration_seconds=duration,
                error_message=str(e)
            )
    
    async def _retry_recovery(
        self,
        action: RecoveryAction,
        operation_func: Callable[..., Any],
        *args,
        **kwargs
    ) -> RecoveryResult:
        """Attempt recovery using retry strategy."""
        for attempt in range(action.max_attempts):
            try:
                self.logger.debug(f"Recovery retry attempt {attempt + 1}/{action.max_attempts}")
                
                result = await asyncio.wait_for(
                    operation_func(*args, **kwargs),
                    timeout=action.timeout_seconds
                )
                
                self.logger.info(f"Recovery succeeded on attempt {attempt + 1}")
                return RecoveryResult(
                    success=True,
                    strategy_used=RecoveryStrategy.RETRY,
                    attempts_made=attempt + 1,
                    duration_seconds=0.0,  # Will be set by caller
                    result=result
                )
                
            except Exception as e:
                if attempt < action.max_attempts - 1:
                    self.logger.warning(f"Recovery attempt {attempt + 1} failed: {e}")
                    await asyncio.sleep(action.delay_seconds)
                else:
                    self.logger.error(f"All recovery attempts failed: {e}")
        
        return RecoveryResult(
            success=False,
            strategy_used=RecoveryStrategy.RETRY,
            attempts_made=action.max_attempts,
            duration_seconds=0.0,
            error_message="All retry attempts failed"
        )
    
    async def _fallback_recovery(
        self,
        action: RecoveryAction,
        operation_func: Callable[..., Any],
        *args,
        **kwargs
    ) -> RecoveryResult:
        """Attempt recovery using fallback strategy."""
        self.logger.info("Using fallback recovery strategy")
        
        return RecoveryResult(
            success=True,
            strategy_used=RecoveryStrategy.FALLBACK,
            attempts_made=1,
            duration_seconds=0.0,
            result=action.fallback_value
        )
    
    async def _graceful_degrade_recovery(
        self,
        action: RecoveryAction,
        operation_func: Callable[..., Any],
        *args,
        **kwargs
    ) -> RecoveryResult:
        """Attempt recovery using graceful degradation."""
        self.logger.info("Using graceful degradation recovery strategy")
        
        # Return a simplified/degraded version of the expected result
        degraded_result = {
            "status": "degraded",
            "message": "Service operating in degraded mode",
            "data": action.fallback_value
        }
        
        return RecoveryResult(
            success=True,
            strategy_used=RecoveryStrategy.GRACEFUL_DEGRADE,
            attempts_made=1,
            duration_seconds=0.0,
            result=degraded_result
        )
    
    def get_recovery_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get recovery statistics."""
        stats = {}
        
        for error_type, counts in self._recovery_stats.items():
            total_attempts = counts['attempts']
            success_rate = 0.0
            
            if total_attempts > 0:
                success_rate = (counts['successes'] / total_attempts) * 100.0
            
            stats[error_type] = {
                'total_attempts': total_attempts,
                'successes': counts['successes'],
                'failures': counts['failures'],
                'success_rate_percent': round(success_rate, 2),
                'recovery_action': self._recovery_actions.get(error_type, {})
            }
        
        return stats
    
    def clear_stats(self) -> None:
        """Clear recovery statistics."""
        for error_type in self._recovery_stats:
            self._recovery_stats[error_type] = {
                'attempts': 0,
                'successes': 0,
                'failures': 0
            }
        
        self.logger.info("Recovery statistics cleared")


# Global auto recovery instance
_auto_recovery = AutoRecovery()


def get_auto_recovery() -> AutoRecovery:
    """Get global auto recovery instance."""
    return _auto_recovery


def recovery_handler(
    error_type: str,
    strategy: RecoveryStrategy = RecoveryStrategy.RETRY,
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    fallback_value: Optional[Any] = None
):
    """
    Decorator to add automatic recovery to functions.
    
    Args:
        error_type: Exception class name to handle
        strategy: Recovery strategy to use
        max_attempts: Maximum recovery attempts
        delay_seconds: Delay between attempts
        fallback_value: Fallback value for fallback strategy
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # Register recovery action
        action = RecoveryAction(
            strategy=strategy,
            max_attempts=max_attempts,
            delay_seconds=delay_seconds,
            fallback_value=fallback_value
        )
        
        _auto_recovery.register_recovery_action(error_type, action)
        
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                from .error_context import create_error_context
                
                # Create error context
                error_context = create_error_context(
                    error=e,
                    operation=func.__name__,
                    component=func.__module__
                )
                
                # Attempt recovery
                recovery_result = await _auto_recovery.attempt_recovery(
                    error_context, func, *args, **kwargs
                )
                
                if recovery_result.success:
                    return recovery_result.result
                else:
                    # Re-raise original exception if recovery failed
                    raise
        
        def sync_wrapper(*args, **kwargs):
            # For sync functions, convert to async temporarily
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(async_wrapper(*args, **kwargs))
            except RuntimeError:
                return asyncio.run(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
