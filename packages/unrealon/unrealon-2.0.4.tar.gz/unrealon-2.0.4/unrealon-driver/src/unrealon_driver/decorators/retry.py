"""
Clean retry decorator with exponential backoff.
"""

import asyncio
import logging
from functools import wraps
from typing import Callable, Type, Tuple, Optional

logger = logging.getLogger(__name__)


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Clean retry decorator.
    
    Automatically retries function on specified exceptions
    with exponential backoff.
    
    Args:
        max_attempts: Maximum retry attempts
        delay: Initial delay between retries
        backoff: Backoff multiplier for delay
        exceptions: Exception types to retry on
        on_retry: Callback function called on each retry
    """
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            """Async retry wrapper."""
            
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        # Last attempt failed
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    
                    # Log retry attempt
                    logger.warning(f"Function {func.__name__} attempt {attempt + 1} failed: {e}. Retrying in {current_delay}s...")
                    
                    # Call retry callback if provided
                    if on_retry:
                        try:
                            if asyncio.iscoroutinefunction(on_retry):
                                await on_retry(attempt + 1, e)
                            else:
                                on_retry(attempt + 1, e)
                        except Exception as callback_error:
                            logger.error(f"Retry callback error: {callback_error}")
                    
                    # Wait before retry
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            
            # Should never reach here, but just in case
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            """Sync retry wrapper."""
            
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        # Last attempt failed
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    
                    # Log retry attempt
                    logger.warning(f"Function {func.__name__} attempt {attempt + 1} failed: {e}. Retrying in {current_delay}s...")
                    
                    # Call retry callback if provided
                    if on_retry:
                        try:
                            on_retry(attempt + 1, e)
                        except Exception as callback_error:
                            logger.error(f"Retry callback error: {callback_error}")
                    
                    # Wait before retry (sync)
                    import time
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            # Should never reach here, but just in case
            raise last_exception
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
