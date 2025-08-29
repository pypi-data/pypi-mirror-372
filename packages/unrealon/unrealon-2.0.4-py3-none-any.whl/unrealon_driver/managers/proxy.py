"""
Clean proxy manager.
"""

import asyncio
import random
from typing import List, Optional, Dict, Any
from pydantic import Field

from .base import BaseManager, ManagerConfig


class ProxyManagerConfig(ManagerConfig):
    """Proxy manager configuration."""
    proxies: List[str] = Field(default_factory=list, description="List of proxy URLs")
    rotation_interval: int = Field(default=300, description="Rotation interval seconds")
    health_check_interval: int = Field(default=60, description="Health check interval")


class ProxyManager(BaseManager):
    """Simple proxy rotation manager."""
    
    def __init__(self, config: ProxyManagerConfig):
        super().__init__(config, "proxy")
        self.config: ProxyManagerConfig = config
        self.active_proxies: List[str] = []
        self.current_proxy: Optional[str] = None
        self._rotation_task: Optional[asyncio.Task] = None
    
    async def _initialize(self) -> bool:
        """Initialize proxy manager."""
        self.active_proxies = self.config.proxies.copy()
        
        if self.active_proxies:
            self.current_proxy = random.choice(self.active_proxies)
            # Start rotation task
            self._rotation_task = asyncio.create_task(self._rotation_loop())
        
        return True
    
    async def _shutdown(self):
        """Shutdown proxy manager."""
        if self._rotation_task:
            self._rotation_task.cancel()
            try:
                await self._rotation_task
            except asyncio.CancelledError:
                pass
    
    async def _rotation_loop(self):
        """Background proxy rotation."""
        while True:
            try:
                await asyncio.sleep(self.config.rotation_interval)
                
                if self.active_proxies:
                    old_proxy = self.current_proxy
                    self.current_proxy = random.choice(self.active_proxies)
                    
                    if old_proxy != self.current_proxy:
                        self.logger.info(f"Rotated proxy: {old_proxy} -> {self.current_proxy}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Proxy rotation error: {e}")
    
    def get_proxy(self) -> Optional[str]:
        """Get current proxy."""
        return self.current_proxy
    
    def get_proxy_dict(self) -> Optional[Dict[str, str]]:
        """Get proxy as dict for requests."""
        if not self.current_proxy:
            return None
        
        return {
            "http": self.current_proxy,
            "https": self.current_proxy
        }
    
    def mark_proxy_bad(self, proxy: str):
        """Mark proxy as bad and remove from rotation."""
        if proxy in self.active_proxies:
            self.active_proxies.remove(proxy)
            self.logger.warning(f"Removed bad proxy: {proxy}")
            
            # Switch to new proxy if current is bad
            if proxy == self.current_proxy and self.active_proxies:
                self.current_proxy = random.choice(self.active_proxies)
    
    async def _health_check(self) -> Dict[str, Any]:
        """Proxy health check."""
        return {
            "status": "ok",
            "current_proxy": self.current_proxy,
            "active_proxies": len(self.active_proxies),
            "total_proxies": len(self.config.proxies)
        }
