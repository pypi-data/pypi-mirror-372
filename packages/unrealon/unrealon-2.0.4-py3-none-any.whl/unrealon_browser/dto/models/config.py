"""
Browser DTOs - Configuration Models

Configuration models for browser automation.
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from .enums import BrowserType, BrowserMode

from unrealon_core.config import get_url_config


def _get_default_stealth_url() -> str:
    """Get default stealth test URL based on environment configuration."""
    return get_url_config().stealth_test_url


class BrowserConfig(BaseModel):
    """Simplified browser configuration."""

    model_config = ConfigDict(extra="forbid")

    # Basic settings
    browser_type: BrowserType = Field(default=BrowserType.CHROMIUM)
    mode: BrowserMode = Field(default=BrowserMode.AUTO)

    # Timeouts
    page_load_timeout_seconds: float = Field(default=30.0)
    navigation_timeout_seconds: float = Field(default=30.0)

    # Proxy settings
    use_proxy_rotation: bool = Field(default=True)
    realistic_ports_only: bool = Field(default=False)
    parser_name: str = Field(default="default_parser")
    parser_id: Optional[str] = Field(default=None, description="Optional parser ID for logging")

    # Performance
    disable_images: bool = Field(default=False)
    
    # Stealth settings
    stealth_warmup_enabled: bool = Field(default=True, description="Enable stealth warmup before target navigation")
    stealth_test_url: str = Field(default_factory=_get_default_stealth_url, description="URL for stealth warmup")
    stealth_warmup_delay: float = Field(default=3.0, description="Delay in seconds after stealth warmup")
    stealth_retry_attempts: int = Field(default=2, description="Maximum retry attempts for failed navigation")
    stealth_retry_delay: float = Field(default=3.0, description="Delay between retry attempts")
