"""
Clean task decorator for registering task handlers.
"""

import asyncio
import logging
from functools import wraps
from typing import Callable, Any, Optional

from unrealon_core.models.websocket import TaskAssignmentData, TaskResultData
from unrealon_core.enums import TaskStatus

logger = logging.getLogger(__name__)


def task(task_type: str, description: Optional[str] = None):
    """
    Clean task decorator.
    
    Registers a function as a task handler and provides
    automatic error handling and result formatting.
    
    Args:
        task_type: Type of task this handler processes
        description: Optional description of the task
    """
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(task_data: TaskAssignmentData, *args, **kwargs) -> Any:
            """Task wrapper with error handling."""
            
            start_time = asyncio.get_event_loop().time()
            
            try:
                logger.info(f"Starting task {task_type}: {task_data.task_id}")
                
                # Execute the task function
                if asyncio.iscoroutinefunction(func):
                    result = await func(task_data, *args, **kwargs)
                else:
                    result = func(task_data, *args, **kwargs)
                
                duration = asyncio.get_event_loop().time() - start_time
                logger.info(f"Task {task_type} completed in {duration:.2f}s: {task_data.task_id}")
                
                return result
                
            except Exception as e:
                duration = asyncio.get_event_loop().time() - start_time
                logger.error(f"Task {task_type} failed after {duration:.2f}s: {task_data.task_id} - {e}")
                raise
        
        # Store task metadata
        wrapper._task_type = task_type
        wrapper._task_description = description
        wrapper._is_task_handler = True
        
        return wrapper
    
    return decorator
