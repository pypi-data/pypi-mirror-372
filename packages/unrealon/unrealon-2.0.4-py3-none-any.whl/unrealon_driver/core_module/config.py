"""
Clean module configuration.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ModuleConfig(BaseModel):
    """Base configuration for all modules."""
    
    # Module identification
    module_name: str = Field(..., description="Unique module name")
    version: str = Field(default="1.0.0", description="Module version")
    
    # Module behavior
    enabled: bool = Field(default=True, description="Whether module is enabled")
    auto_start: bool = Field(default=True, description="Auto-start on driver init")
    
    # Performance
    timeout_seconds: float = Field(default=30.0, description="Operation timeout")
    retry_count: int = Field(default=3, description="Retry attempts")
    
    # Health checks
    health_check_interval: int = Field(default=60, description="Health check interval")
    
    # Custom settings
    custom_settings: Dict[str, Any] = Field(default_factory=dict, description="Module-specific settings")
    
    model_config = {"extra": "forbid"}
