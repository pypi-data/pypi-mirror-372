"""
Clean cache manager.
"""

import asyncio
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from pydantic import Field

from ..utils.time import utc_now
from .base import BaseManager, ManagerConfig


class CacheManagerConfig(ManagerConfig):
    """Cache manager configuration."""
    default_ttl: int = Field(default=3600, description="Default TTL seconds")
    max_size: int = Field(default=1000, description="Max cache entries")


class CacheEntry:
    """Cache entry with TTL."""
    
    def __init__(self, value: Any, ttl: int):
        self.value = value
        self.expires_at = utc_now() + timedelta(seconds=ttl)
    
    def is_expired(self) -> bool:
        """Check if entry is expired."""
        return utc_now() > self.expires_at


class CacheManager(BaseManager):
    """Simple in-memory cache manager."""
    
    def __init__(self, config: CacheManagerConfig):
        super().__init__(config, "cache")
        self.config: CacheManagerConfig = config
        self._cache: Dict[str, CacheEntry] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def _initialize(self) -> bool:
        """Initialize cache."""
        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_expired())
        return True
    
    async def _shutdown(self):
        """Shutdown cache."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        self._cache.clear()
    
    async def _cleanup_expired(self):
        """Background task to clean expired entries."""
        while True:
            try:
                await asyncio.sleep(60)  # Cleanup every minute
                
                expired_keys = []
                for key, entry in self._cache.items():
                    if entry.is_expired():
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self._cache[key]
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Cache cleanup error: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        entry = self._cache.get(key)
        if not entry:
            return None
        
        if entry.is_expired():
            del self._cache[key]
            return None
        
        return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        if len(self._cache) >= self.config.max_size:
            # Remove oldest entry
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        ttl = ttl or self.config.default_ttl
        self._cache[key] = CacheEntry(value, ttl)
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
    
    async def _health_check(self) -> Dict[str, Any]:
        """Cache health check."""
        return {
            "status": "ok",
            "entries": len(self._cache),
            "max_size": self.config.max_size
        }
