"""
Clean base manager system.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field

from ..utils.time import utc_now

logger = logging.getLogger(__name__)


class ManagerStatus(str, Enum):
    """Manager lifecycle status."""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"
    SHUTDOWN = "shutdown"


class ManagerConfig(BaseModel):
    """Base configuration for all managers."""
    enabled: bool = Field(default=True, description="Whether manager is enabled")
    timeout: int = Field(default=30, description="Operation timeout seconds")
    max_retries: int = Field(default=3, description="Max retry attempts")
    log_level: str = Field(default="INFO", description="Logging level")
    
    model_config = {"extra": "forbid"}


class ManagerStats(BaseModel):
    """Manager operation statistics."""
    operations_total: int = 0
    operations_successful: int = 0
    operations_failed: int = 0
    last_operation: Optional[datetime] = None
    average_duration: float = 0.0
    
    def record_operation(self, success: bool, duration: float):
        """Record operation result."""
        self.operations_total += 1
        if success:
            self.operations_successful += 1
        else:
            self.operations_failed += 1
        
        self.last_operation = utc_now()
        
        # Simple moving average
        if self.operations_total == 1:
            self.average_duration = duration
        else:
            self.average_duration = (
                (self.average_duration * (self.operations_total - 1) + duration) 
                / self.operations_total
            )
    
    def get_success_rate(self) -> float:
        """Get success rate percentage."""
        if self.operations_total == 0:
            return 0.0
        return (self.operations_successful / self.operations_total) * 100.0


class BaseManager(ABC):
    """
    Clean base manager class.
    
    Provides common functionality for all managers:
    - Lifecycle management
    - Statistics tracking
    - Error handling
    - Health checks
    """
    
    def __init__(self, config: ManagerConfig, name: str):
        self.config = config
        self.name = name
        self.status = ManagerStatus.UNINITIALIZED
        self.stats = ManagerStats()
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
        # Set log level
        if hasattr(logging, config.log_level):
            self.logger.setLevel(getattr(logging, config.log_level))
    
    async def initialize(self) -> bool:
        """Initialize manager."""
        if not self.config.enabled:
            self.logger.info(f"Manager {self.name} is disabled")
            self.status = ManagerStatus.SHUTDOWN
            return True
        
        try:
            self.status = ManagerStatus.INITIALIZING
            self.logger.info(f"Initializing manager: {self.name}")
            
            success = await self._initialize()
            
            if success:
                self.status = ManagerStatus.READY
                self.logger.info(f"Manager {self.name} initialized successfully")
            else:
                self.status = ManagerStatus.ERROR
                self.logger.error(f"Manager {self.name} initialization failed")
            
            return success
            
        except Exception as e:
            self.status = ManagerStatus.ERROR
            self.logger.error(f"Manager {self.name} initialization error: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown manager."""
        try:
            self.status = ManagerStatus.SHUTTING_DOWN
            self.logger.info(f"Shutting down manager: {self.name}")
            
            await self._shutdown()
            
            self.status = ManagerStatus.SHUTDOWN
            self.logger.info(f"Manager {self.name} shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Manager {self.name} shutdown error: {e}")
            self.status = ManagerStatus.ERROR
    
    @abstractmethod
    async def _initialize(self) -> bool:
        """Manager-specific initialization."""
        pass
    
    @abstractmethod
    async def _shutdown(self):
        """Manager-specific shutdown."""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            health_data = await self._health_check()
            
            return {
                "name": self.name,
                "status": self.status.value,
                "enabled": self.config.enabled,
                "stats": self.stats.model_dump(),
                "health": health_data
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed for {self.name}: {e}")
            return {
                "name": self.name,
                "status": "error",
                "error": str(e)
            }
    
    async def _health_check(self) -> Dict[str, Any]:
        """Manager-specific health check."""
        return {"status": "ok"}
    
    def is_ready(self) -> bool:
        """Check if manager is ready."""
        return self.status == ManagerStatus.READY
