"""
Clean schedule decorator for cron-like scheduling.
"""

import asyncio
import logging
from functools import wraps
from typing import Callable, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def schedule(
    interval: Optional[int] = None,
    cron: Optional[str] = None,
    run_once: bool = False,
    start_immediately: bool = False
):
    """
    Clean schedule decorator.
    
    Schedules function execution at specified intervals or cron patterns.
    
    Args:
        interval: Interval in seconds between executions
        cron: Cron expression (simple format: "*/5 * * * *" for every 5 minutes)
        run_once: Run only once then stop
        start_immediately: Start immediately instead of waiting for first interval
    """
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            """Scheduled function wrapper."""
            
            if not interval and not cron:
                raise ValueError("Either interval or cron must be specified")
            
            execution_count = 0
            
            # Start immediately if requested
            if start_immediately:
                try:
                    logger.info(f"Executing scheduled function {func.__name__} (immediate start)")
                    
                    if asyncio.iscoroutinefunction(func):
                        await func(*args, **kwargs)
                    else:
                        func(*args, **kwargs)
                    
                    execution_count += 1
                    
                    if run_once:
                        logger.info(f"Scheduled function {func.__name__} completed (run_once=True)")
                        return
                        
                except Exception as e:
                    logger.error(f"Scheduled function {func.__name__} failed: {e}")
            
            # Main scheduling loop
            while True:
                try:
                    # Calculate next execution time
                    if interval:
                        await asyncio.sleep(interval)
                    elif cron:
                        # Simple cron parsing (just for intervals like "*/5 * * * *")
                        next_delay = _parse_simple_cron(cron)
                        await asyncio.sleep(next_delay)
                    
                    # Execute function
                    logger.debug(f"Executing scheduled function {func.__name__}")
                    
                    if asyncio.iscoroutinefunction(func):
                        await func(*args, **kwargs)
                    else:
                        func(*args, **kwargs)
                    
                    execution_count += 1
                    
                    if run_once:
                        logger.info(f"Scheduled function {func.__name__} completed after {execution_count} executions")
                        break
                        
                except asyncio.CancelledError:
                    logger.info(f"Scheduled function {func.__name__} cancelled after {execution_count} executions")
                    break
                except Exception as e:
                    logger.error(f"Scheduled function {func.__name__} failed: {e}")
                    # Continue scheduling even if execution fails
        
        # Store schedule metadata
        wrapper._schedule_interval = interval
        wrapper._schedule_cron = cron
        wrapper._schedule_run_once = run_once
        wrapper._is_scheduled = True
        
        return wrapper
    
    return decorator


def _parse_simple_cron(cron_expr: str) -> int:
    """
    Parse simple cron expressions.
    
    Currently supports only basic interval patterns like:
    - "*/5 * * * *" (every 5 minutes)
    - "0 * * * *" (every hour)
    - "0 0 * * *" (every day)
    
    Returns delay in seconds until next execution.
    """
    
    parts = cron_expr.strip().split()
    if len(parts) != 5:
        raise ValueError(f"Invalid cron expression: {cron_expr}")
    
    minute, hour, day, month, weekday = parts
    
    # Simple parsing for common patterns
    if minute.startswith("*/"):
        # Every N minutes
        interval_minutes = int(minute[2:])
        return interval_minutes * 60
    elif minute == "0" and hour.startswith("*/"):
        # Every N hours
        interval_hours = int(hour[2:])
        return interval_hours * 3600
    elif minute == "0" and hour == "0":
        # Daily
        return 24 * 3600
    else:
        # Default to 5 minutes for unsupported patterns
        logger.warning(f"Unsupported cron pattern {cron_expr}, defaulting to 5 minutes")
        return 300
