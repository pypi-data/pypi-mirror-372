"""
Clean threading manager.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Optional, Dict
from pydantic import Field

from .base import BaseManager, ManagerConfig


class ThreadManagerConfig(ManagerConfig):
    """Thread manager configuration."""
    max_workers: int = Field(default=4, description="Max thread workers")


class ThreadManager(BaseManager):
    """Simple thread pool manager."""
    
    def __init__(self, config: ThreadManagerConfig):
        super().__init__(config, "threading")
        self.config: ThreadManagerConfig = config
        self.executor: Optional[ThreadPoolExecutor] = None
    
    async def _initialize(self) -> bool:
        """Initialize thread pool."""
        self.executor = ThreadPoolExecutor(
            max_workers=self.config.max_workers,
            thread_name_prefix="unrealon-driver"
        )
        return True
    
    async def _shutdown(self):
        """Shutdown thread pool."""
        if self.executor:
            self.executor.shutdown(wait=True)
            self.executor = None
    
    async def run_in_thread(self, func: Callable, *args, **kwargs) -> Any:
        """Run function in thread pool."""
        if not self.executor:
            raise RuntimeError("Thread manager not initialized")
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args, **kwargs)
    
    async def _health_check(self) -> Dict[str, Any]:
        """Thread manager health check."""
        return {
            "status": "ok",
            "max_workers": self.config.max_workers,
            "active": self.executor is not None
        }
