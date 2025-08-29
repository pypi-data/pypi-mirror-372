"""
URL configuration management.

Provides centralized URL management with environment-specific endpoints.
"""

from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from .environment import get_environment_config, Environment


class URLConfig(BaseModel):
    """URL configuration for different services."""
    
    model_config = ConfigDict(
        # Add any specific config here if needed
    )
    
    # Scanner/Detection URLs
    scanner_url: str = Field(
        description="URL for browser detection and stealth testing"
    )
    
    # Cloud platform URLs  
    cloud_base_url: str = Field(
        description="Base URL for UnrealOn Cloud platform"
    )
    
    # API endpoints
    api_base_url: str = Field(
        description="Base URL for API endpoints"
    )
    
    @classmethod
    def for_environment(cls, environment: Optional[Environment] = None) -> "URLConfig":
        """Create URL config for specific environment."""
        if environment is None:
            environment = get_environment_config().environment
        
        if environment == Environment.PRODUCTION:
            return cls(
                scanner_url="https://cloud.unrealon.com/scanner",
                cloud_base_url="https://cloud.unrealon.com",
                api_base_url="https://api.unrealon.com"
            )
        elif environment == Environment.TESTING:
            return cls(
                scanner_url="https://staging.unrealon.com/scanner", 
                cloud_base_url="https://staging.unrealon.com",
                api_base_url="https://api-staging.unrealon.com"
            )
        else:  # Development
            return cls(
                scanner_url="http://localhost:3000/scanner",
                cloud_base_url="http://localhost:3000", 
                api_base_url="http://localhost:8000"
            )
    
    @property
    def stealth_test_url(self) -> str:
        """Get the URL for stealth testing (replaces bot.sannysoft.com)."""
        return self.scanner_url
    
    @property
    def detection_test_url(self) -> str:
        """Get the URL for browser detection testing."""
        return self.scanner_url


# Global config instance
_url_config: Optional[URLConfig] = None


def get_url_config() -> URLConfig:
    """Get the global URL configuration."""
    global _url_config
    
    if _url_config is None:
        _url_config = URLConfig.for_environment()
    
    return _url_config


def set_url_config(config: URLConfig) -> None:
    """Set the global URL configuration."""
    global _url_config
    _url_config = config


def reset_url_config() -> None:
    """Reset URL config to reload from environment."""
    global _url_config
    _url_config = None
