"""
Clean manager registry.
"""

import asyncio
from typing import Dict, List, Any, Optional
from .base import BaseManager


class ManagerRegistry:
    """
    Clean registry for managing all driver managers.
    
    Provides centralized lifecycle management and health monitoring.
    """
    
    def __init__(self):
        self.managers: Dict[str, BaseManager] = {}
        self._initialized = False
    
    def register(self, manager: BaseManager):
        """Register a manager."""
        self.managers[manager.name] = manager
    
    def get(self, name: str) -> Optional[BaseManager]:
        """Get manager by name."""
        return self.managers.get(name)
    
    async def initialize_all(self) -> bool:
        """Initialize all registered managers."""
        if self._initialized:
            return True
        
        success_count = 0
        
        for name, manager in self.managers.items():
            try:
                if await manager.initialize():
                    success_count += 1
                else:
                    print(f"Manager {name} initialization failed")
            except Exception as e:
                print(f"Manager {name} initialization error: {e}")
        
        self._initialized = success_count == len(self.managers)
        return self._initialized
    
    async def shutdown_all(self):
        """Shutdown all managers."""
        for name, manager in self.managers.items():
            try:
                await manager.shutdown()
            except Exception as e:
                print(f"Manager {name} shutdown error: {e}")
        
        self._initialized = False
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Get health status of all managers."""
        health_data = {}
        
        for name, manager in self.managers.items():
            try:
                health_data[name] = await manager.health_check()
            except Exception as e:
                health_data[name] = {
                    "name": name,
                    "status": "error",
                    "error": str(e)
                }
        
        return {
            "managers": health_data,
            "total": len(self.managers),
            "initialized": self._initialized
        }
    
    def get_ready_managers(self) -> List[str]:
        """Get list of ready manager names."""
        return [
            name for name, manager in self.managers.items()
            if manager.is_ready()
        ]
    
    def is_all_ready(self) -> bool:
        """Check if all managers are ready."""
        return all(manager.is_ready() for manager in self.managers.values())
