"""
Clean driver configuration without hardcoded values.
"""

import os
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, computed_field


class DriverMode(str, Enum):
    """Driver operation modes."""
    STANDALONE = "standalone"
    DAEMON = "daemon"


class DriverConfig(BaseModel):
    """
    Clean driver configuration.
    No hardcoded presets - user configures everything explicitly.
    """
    
    # Basic settings
    name: str = Field(..., description="Driver name")
    mode: DriverMode = Field(default=DriverMode.STANDALONE, description="Operation mode")
    
    # WebSocket connection (auto-detected)
    websocket_url: Optional[str] = Field(default=None, description="Manual WebSocket URL override")
    websocket_timeout: int = Field(default=30, description="WebSocket timeout seconds")
    
    @computed_field
    @property
    def effective_websocket_url(self) -> Optional[str]:
        """
        Auto-detect WebSocket URL from multiple sources.
        
        Priority:
        1. Explicit websocket_url field
        2. Environment variable UNREALON_WEBSOCKET_URL  
        3. Environment variable UNREALON_WS_URL
        4. Default localhost for development
        """
        # 1. Explicit override
        if self.websocket_url:
            return self.websocket_url
        
        # 2. Environment variables
        env_url = (
            os.getenv('UNREALON_WEBSOCKET_URL') or 
            os.getenv('UNREALON_WS_URL') or
            os.getenv('WS_URL')
        )
        if env_url:
            return env_url
        
        # 3. No default - return None if nothing is configured
        return None
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    
    # HTTP settings
    http_timeout: int = Field(default=30, description="HTTP timeout seconds")
    max_retries: int = Field(default=3, description="Max HTTP retries")
    
    # Browser settings
    browser_headless: bool = Field(default=True, description="Run browser headless")
    browser_timeout: int = Field(default=30, description="Browser timeout seconds")
    
    # Proxy settings
    proxy_enabled: bool = Field(default=False, description="Enable proxy rotation")
    proxy_rotation_interval: int = Field(default=300, description="Proxy rotation seconds")
    
    # Cache settings
    cache_enabled: bool = Field(default=True, description="Enable response caching")
    cache_ttl: int = Field(default=3600, description="Cache TTL seconds")
    
    # Threading
    max_workers: int = Field(default=4, description="Max thread workers")
    
    # Performance
    batch_size: int = Field(default=10, description="Batch processing size")
    
    model_config = {"extra": "forbid"}
