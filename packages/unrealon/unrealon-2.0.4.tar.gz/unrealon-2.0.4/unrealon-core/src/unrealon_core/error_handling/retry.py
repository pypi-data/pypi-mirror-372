"""
Retry System

Advanced retry logic with multiple backoff strategies.
Following critical requirements - max 500 lines, functions < 20 lines.

Phase 2: Core Systems - Error Handling
"""

import asyncio
import logging
import random
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Callable, Optional, Type, Union, List
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict

from ..exceptions.base import UnrealOnError
from ..utils.time import utc_now


logger = logging.getLogger(__name__)


class RetryStrategy(str, Enum):
    """Retry strategy types."""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"


class RetryResult(BaseModel):
    """Result of retry operation."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    success: bool = Field(description="Whether operation succeeded")
    attempts: int = Field(description="Number of attempts made")
    total_duration: float = Field(description="Total duration in seconds")
    last_error: Optional[str] = Field(default=None, description="Last error message")
    result: Optional[Any] = Field(default=None, description="Operation result if successful")


class RetryConfig(BaseModel):
    """Configuration for retry behavior."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    max_attempts: int = Field(default=3, ge=1, le=10, description="Maximum retry attempts")
    strategy: RetryStrategy = Field(default=RetryStrategy.EXPONENTIAL, description="Backoff strategy")
    base_delay: float = Field(default=1.0, ge=0.1, le=60.0, description="Base delay in seconds")
    max_delay: float = Field(default=60.0, ge=1.0, le=300.0, description="Maximum delay in seconds")
    jitter: bool = Field(default=True, description="Add random jitter to delays")
    retryable_exceptions: List[str] = Field(
        default_factory=lambda: ["ConnectionError", "TimeoutError", "HTTPError"],
        description="Exception types that should trigger retry"
    )


class BackoffCalculator(ABC):
    """Abstract base for backoff calculation strategies."""
    
    def __init__(self, config: RetryConfig):
        self.config = config
    
    @abstractmethod
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number."""
        pass
    
    def add_jitter(self, delay: float) -> float:
        """Add random jitter to delay."""
        if not self.config.jitter:
            return delay
        
        # Add ±25% jitter
        jitter_range = delay * 0.25
        jitter = random.uniform(-jitter_range, jitter_range)
        return max(0.1, delay + jitter)


class ExponentialBackoff(BackoffCalculator):
    """Exponential backoff strategy."""
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay."""
        delay = self.config.base_delay * (2 ** (attempt - 1))
        delay = min(delay, self.config.max_delay)
        return self.add_jitter(delay)


class LinearBackoff(BackoffCalculator):
    """Linear backoff strategy."""
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate linear backoff delay."""
        delay = self.config.base_delay * attempt
        delay = min(delay, self.config.max_delay)
        return self.add_jitter(delay)


class FixedBackoff(BackoffCalculator):
    """Fixed delay backoff strategy."""
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate fixed backoff delay."""
        return self.add_jitter(self.config.base_delay)


def create_backoff_calculator(config: RetryConfig) -> BackoffCalculator:
    """Factory function to create backoff calculator."""
    if config.strategy == RetryStrategy.EXPONENTIAL:
        return ExponentialBackoff(config)
    elif config.strategy == RetryStrategy.LINEAR:
        return LinearBackoff(config)
    else:
        return FixedBackoff(config)


def is_retryable_exception(
    exception: Exception, 
    retryable_types: List[str]
) -> bool:
    """Check if exception is retryable."""
    exception_name = exception.__class__.__name__
    return exception_name in retryable_types


async def retry_async(
    func: Callable[..., Any],
    config: RetryConfig,
    *args,
    **kwargs
) -> RetryResult:
    """
    Execute async function with retry logic.
    
    Args:
        func: Async function to execute
        config: Retry configuration
        *args, **kwargs: Function arguments
        
    Returns:
        RetryResult with operation outcome
    """
    start_time = utc_now()
    backoff = create_backoff_calculator(config)
    last_error = None
    
    for attempt in range(1, config.max_attempts + 1):
        try:
            logger.debug(f"Attempt {attempt}/{config.max_attempts} for {func.__name__}")
            
            result = await func(*args, **kwargs)
            
            duration = (utc_now() - start_time).total_seconds()
            
            if attempt > 1:
                logger.info(f"{func.__name__} succeeded on attempt {attempt}")
            
            return RetryResult(
                success=True,
                attempts=attempt,
                total_duration=duration,
                result=result
            )
            
        except Exception as e:
            last_error = str(e)
            
            if not is_retryable_exception(e, config.retryable_exceptions):
                logger.error(f"{func.__name__} failed with non-retryable error: {e}")
                break
            
            if attempt < config.max_attempts:
                delay = backoff.calculate_delay(attempt)
                logger.warning(
                    f"{func.__name__} attempt {attempt} failed: {e}. "
                    f"Retrying in {delay:.2f}s..."
                )
                await asyncio.sleep(delay)
            else:
                logger.error(f"{func.__name__} failed after {attempt} attempts: {e}")
    
    duration = (utc_now() - start_time).total_seconds()
    
    return RetryResult(
        success=False,
        attempts=config.max_attempts,
        total_duration=duration,
        last_error=last_error
    )


def retry_sync(
    func: Callable[..., Any],
    config: RetryConfig,
    *args,
    **kwargs
) -> RetryResult:
    """
    Execute sync function with retry logic.
    
    Args:
        func: Sync function to execute
        config: Retry configuration
        *args, **kwargs: Function arguments
        
    Returns:
        RetryResult with operation outcome
    """
    import time
    
    start_time = utc_now()
    backoff = create_backoff_calculator(config)
    last_error = None
    
    for attempt in range(1, config.max_attempts + 1):
        try:
            logger.debug(f"Attempt {attempt}/{config.max_attempts} for {func.__name__}")
            
            result = func(*args, **kwargs)
            
            duration = (utc_now() - start_time).total_seconds()
            
            if attempt > 1:
                logger.info(f"{func.__name__} succeeded on attempt {attempt}")
            
            return RetryResult(
                success=True,
                attempts=attempt,
                total_duration=duration,
                result=result
            )
            
        except Exception as e:
            last_error = str(e)
            
            if not is_retryable_exception(e, config.retryable_exceptions):
                logger.error(f"{func.__name__} failed with non-retryable error: {e}")
                break
            
            if attempt < config.max_attempts:
                delay = backoff.calculate_delay(attempt)
                logger.warning(
                    f"{func.__name__} attempt {attempt} failed: {e}. "
                    f"Retrying in {delay:.2f}s..."
                )
                time.sleep(delay)
            else:
                logger.error(f"{func.__name__} failed after {attempt} attempts: {e}")
    
    duration = (utc_now() - start_time).total_seconds()
    
    return RetryResult(
        success=False,
        attempts=config.max_attempts,
        total_duration=duration,
        last_error=last_error
    )
