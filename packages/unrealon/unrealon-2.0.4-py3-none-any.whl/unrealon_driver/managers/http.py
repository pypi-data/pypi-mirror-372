"""
Clean HTTP manager for requests.
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional
from pydantic import Field

from .base import BaseManager, ManagerConfig


class HttpManagerConfig(ManagerConfig):
    """HTTP manager configuration."""
    user_agent: str = Field(default="UnrealOn-Driver/1.0", description="User agent string")
    max_connections: int = Field(default=100, description="Max concurrent connections")
    connector_limit: int = Field(default=30, description="Connector limit per host")


class HttpManager(BaseManager):
    """Clean HTTP manager with aiohttp."""
    
    def __init__(self, config: HttpManagerConfig):
        super().__init__(config, "http")
        self.config: HttpManagerConfig = config
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _initialize(self) -> bool:
        """Initialize HTTP session."""
        try:
            # Create connector
            connector = aiohttp.TCPConnector(
                limit=self.config.max_connections,
                limit_per_host=self.config.connector_limit,
                ttl_dns_cache=300,
                use_dns_cache=True
            )
            
            # Create session
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            headers = {"User-Agent": self.config.user_agent}
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=headers
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"HTTP manager initialization failed: {e}")
            return False
    
    async def _shutdown(self):
        """Shutdown HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make GET request."""
        if not self.session:
            raise RuntimeError("HTTP manager not initialized")
        
        start_time = asyncio.get_event_loop().time()
        success = False
        
        try:
            response = await self.session.get(url, **kwargs)
            success = True
            return response
        finally:
            duration = asyncio.get_event_loop().time() - start_time
            self.stats.record_operation(success, duration)
    
    async def post(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make POST request."""
        if not self.session:
            raise RuntimeError("HTTP manager not initialized")
        
        start_time = asyncio.get_event_loop().time()
        success = False
        
        try:
            response = await self.session.post(url, **kwargs)
            success = True
            return response
        finally:
            duration = asyncio.get_event_loop().time() - start_time
            self.stats.record_operation(success, duration)
    
    async def request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make generic request."""
        if not self.session:
            raise RuntimeError("HTTP manager not initialized")
        
        start_time = asyncio.get_event_loop().time()
        success = False
        
        try:
            response = await self.session.request(method, url, **kwargs)
            success = True
            return response
        finally:
            duration = asyncio.get_event_loop().time() - start_time
            self.stats.record_operation(success, duration)
