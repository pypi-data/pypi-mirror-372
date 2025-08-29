"""
Clean module registry for lifecycle management.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any

from .protocols import BaseModule, ModuleStatus
from .event_manager import EventManager

logger = logging.getLogger(__name__)


class ModuleRegistry:
    """
    Clean module registry.
    
    Manages module lifecycle and provides centralized
    access to all registered modules.
    """
    
    def __init__(self, event_manager: Optional[EventManager] = None):
        self.modules: Dict[str, BaseModule] = {}
        self.event_manager = event_manager or EventManager()
        self._initialized = False
    
    def register(self, module: BaseModule):
        """Register a module."""
        self.modules[module.name] = module
        
        # Set event manager if module supports it
        if hasattr(module, 'set_event_manager'):
            module.set_event_manager(self.event_manager)
        
        logger.info(f"Registered module: {module.name}")
    
    def get(self, name: str) -> Optional[BaseModule]:
        """Get module by name."""
        return self.modules.get(name)
    
    def get_all(self) -> Dict[str, BaseModule]:
        """Get all registered modules."""
        return self.modules.copy()
    
    async def initialize_all(self) -> bool:
        """Initialize all registered modules."""
        if self._initialized:
            return True
        
        # Start event manager
        await self.event_manager.start()
        
        success_count = 0
        
        for name, module in self.modules.items():
            try:
                if await module.initialize():
                    success_count += 1
                    logger.info(f"Module {name} initialized successfully")
                else:
                    logger.error(f"Module {name} initialization failed")
            except Exception as e:
                logger.error(f"Module {name} initialization error: {e}")
        
        self._initialized = success_count == len(self.modules)
        
        if self._initialized:
            logger.info(f"All {len(self.modules)} modules initialized successfully")
        else:
            logger.warning(f"Only {success_count}/{len(self.modules)} modules initialized")
        
        return self._initialized
    
    async def start_all(self) -> bool:
        """Start all initialized modules."""
        if not self._initialized:
            logger.error("Cannot start modules - not all initialized")
            return False
        
        success_count = 0
        
        for name, module in self.modules.items():
            if module.status == ModuleStatus.INITIALIZED:
                try:
                    if await module.start():
                        success_count += 1
                        logger.info(f"Module {name} started successfully")
                    else:
                        logger.error(f"Module {name} start failed")
                except Exception as e:
                    logger.error(f"Module {name} start error: {e}")
        
        logger.info(f"Started {success_count}/{len(self.modules)} modules")
        return success_count > 0
    
    async def stop_all(self):
        """Stop all running modules."""
        for name, module in self.modules.items():
            if module.status == ModuleStatus.RUNNING:
                try:
                    await module.stop()
                    logger.info(f"Module {name} stopped successfully")
                except Exception as e:
                    logger.error(f"Module {name} stop error: {e}")
        
        # Stop event manager
        await self.event_manager.stop()
        
        self._initialized = False
        logger.info("All modules stopped")
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Get health status of all modules."""
        health_data = {}
        
        for name, module in self.modules.items():
            try:
                result = await module.health_check()
                health_data[name] = result.model_dump()
            except Exception as e:
                health_data[name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return {
            "modules": health_data,
            "total": len(self.modules),
            "initialized": self._initialized,
            "event_manager": self.event_manager.get_stats()
        }
    
    def get_running_modules(self) -> List[str]:
        """Get list of running module names."""
        return [
            name for name, module in self.modules.items()
            if module.status == ModuleStatus.RUNNING
        ]
    
    def is_all_running(self) -> bool:
        """Check if all modules are running."""
        return all(
            module.status == ModuleStatus.RUNNING 
            for module in self.modules.values()
        )
