"""
Clean timing decorator for performance monitoring.
"""

import asyncio
import logging
import time
from functools import wraps
from typing import Callable, Optional, Dict, Any

logger = logging.getLogger(__name__)


def timing(
    log_result: bool = True,
    log_level: str = "INFO",
    include_args: bool = False,
    threshold: Optional[float] = None
):
    """
    Clean timing decorator.
    
    Measures and logs function execution time.
    
    Args:
        log_result: Whether to log the timing result
        log_level: Log level for timing messages
        include_args: Include function arguments in log
        threshold: Only log if execution time exceeds threshold (seconds)
    """
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            """Async timing wrapper."""
            
            start_time = asyncio.get_event_loop().time()
            
            try:
                result = await func(*args, **kwargs)
                success = True
                error = None
            except Exception as e:
                result = None
                success = False
                error = str(e)
                raise
            finally:
                end_time = asyncio.get_event_loop().time()
                duration = end_time - start_time
                
                # Log timing if enabled and threshold met
                if log_result and (threshold is None or duration >= threshold):
                    _log_timing(func, duration, success, error, args, kwargs, include_args, log_level)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            """Sync timing wrapper."""
            
            start_time = time.perf_counter()
            
            try:
                result = func(*args, **kwargs)
                success = True
                error = None
            except Exception as e:
                result = None
                success = False
                error = str(e)
                raise
            finally:
                end_time = time.perf_counter()
                duration = end_time - start_time
                
                # Log timing if enabled and threshold met
                if log_result and (threshold is None or duration >= threshold):
                    _log_timing(func, duration, success, error, args, kwargs, include_args, log_level)
            
            return result
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def _log_timing(
    func: Callable,
    duration: float,
    success: bool,
    error: Optional[str],
    args: tuple,
    kwargs: dict,
    include_args: bool,
    log_level: str
):
    """Log timing information."""
    
    # Format duration
    if duration < 0.001:
        duration_str = f"{duration * 1000000:.0f}μs"
    elif duration < 1.0:
        duration_str = f"{duration * 1000:.1f}ms"
    else:
        duration_str = f"{duration:.2f}s"
    
    # Build log message
    status = "✓" if success else "✗"
    message = f"{status} {func.__name__} took {duration_str}"
    
    if error:
        message += f" (failed: {error})"
    
    if include_args:
        args_str = ", ".join([repr(arg) for arg in args])
        kwargs_str = ", ".join([f"{k}={repr(v)}" for k, v in kwargs.items()])
        
        if args_str and kwargs_str:
            message += f" | Args: ({args_str}, {kwargs_str})"
        elif args_str:
            message += f" | Args: ({args_str})"
        elif kwargs_str:
            message += f" | Args: ({kwargs_str})"
    
    # Log at specified level
    log_func = getattr(logger, log_level.lower(), logger.info)
    log_func(message)
