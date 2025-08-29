"""
Clean base module implementation.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from .protocols import ModuleStatus, HealthStatus, HealthCheckResult, ModuleEvent, EventType
from .config import ModuleConfig
from ..utils.time import utc_now

logger = logging.getLogger(__name__)


class DriverModule(ABC):
    """
    Clean base module implementation.
    
    Provides common functionality for all driver modules.
    """
    
    def __init__(self, config: ModuleConfig, driver_id: str):
        self.config = config
        self.driver_id = driver_id
        self.name = config.module_name
        self.status = ModuleStatus.UNINITIALIZED
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        
        # Event system
        self.event_manager: Optional[Any] = None
    
    async def initialize(self) -> bool:
        """Initialize module."""
        if not self.config.enabled:
            self.logger.info(f"Module {self.name} is disabled")
            self.status = ModuleStatus.STOPPED
            return True
        
        try:
            self.status = ModuleStatus.INITIALIZING
            self.logger.info(f"Initializing module: {self.name}")
            
            success = await self._initialize()
            
            if success:
                self.status = ModuleStatus.INITIALIZED
                self.logger.info(f"Module {self.name} initialized successfully")
                
                # Emit event
                await self._emit_event(EventType.MODULE_INITIALIZED)
            else:
                self.status = ModuleStatus.ERROR
                self.logger.error(f"Module {self.name} initialization failed")
            
            return success
            
        except Exception as e:
            self.status = ModuleStatus.ERROR
            self.logger.error(f"Module {self.name} initialization error: {e}")
            await self._emit_event(EventType.MODULE_ERROR, error=str(e))
            return False
    
    async def start(self) -> bool:
        """Start module."""
        if self.status != ModuleStatus.INITIALIZED:
            self.logger.error(f"Cannot start module {self.name} - not initialized")
            return False
        
        try:
            self.status = ModuleStatus.STARTING
            self.logger.info(f"Starting module: {self.name}")
            
            success = await self._start()
            
            if success:
                self.status = ModuleStatus.RUNNING
                self.logger.info(f"Module {self.name} started successfully")
                
                # Emit event
                await self._emit_event(EventType.MODULE_STARTED)
            else:
                self.status = ModuleStatus.ERROR
                self.logger.error(f"Module {self.name} start failed")
            
            return success
            
        except Exception as e:
            self.status = ModuleStatus.ERROR
            self.logger.error(f"Module {self.name} start error: {e}")
            await self._emit_event(EventType.MODULE_ERROR, error=str(e))
            return False
    
    async def stop(self) -> None:
        """Stop module."""
        try:
            self.status = ModuleStatus.STOPPING
            self.logger.info(f"Stopping module: {self.name}")
            
            await self._stop()
            
            self.status = ModuleStatus.STOPPED
            self.logger.info(f"Module {self.name} stopped successfully")
            
            # Emit event
            await self._emit_event(EventType.MODULE_STOPPED)
            
        except Exception as e:
            self.status = ModuleStatus.ERROR
            self.logger.error(f"Module {self.name} stop error: {e}")
            await self._emit_event(EventType.MODULE_ERROR, error=str(e))
    
    async def health_check(self) -> HealthCheckResult:
        """Perform health check."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            health_data = await self._health_check()
            
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                timestamp=utc_now(),
                details=health_data,
                response_time_ms=response_time
            )
            
        except Exception as e:
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                timestamp=utc_now(),
                error=str(e),
                response_time_ms=response_time
            )
    
    def set_event_manager(self, event_manager):
        """Set event manager for event emission."""
        self.event_manager = event_manager
    
    async def _emit_event(self, event_type: EventType, data: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        """Emit module event."""
        if not self.event_manager:
            return
        
        try:
            event = ModuleEvent(
                event_type=event_type,
                module_name=self.name,
                timestamp=utc_now(),
                data=data or {},
                error=error
            )
            
            await self.event_manager.emit(event)
            
        except Exception as e:
            self.logger.error(f"Failed to emit event: {e}")
    
    @abstractmethod
    async def _initialize(self) -> bool:
        """Module-specific initialization."""
        pass
    
    @abstractmethod
    async def _start(self) -> bool:
        """Module-specific start logic."""
        pass
    
    @abstractmethod
    async def _stop(self) -> None:
        """Module-specific stop logic."""
        pass
    
    async def _health_check(self) -> Dict[str, Any]:
        """Module-specific health check."""
        return {
            "status": "ok",
            "module": self.name,
            "version": self.config.version
        }
