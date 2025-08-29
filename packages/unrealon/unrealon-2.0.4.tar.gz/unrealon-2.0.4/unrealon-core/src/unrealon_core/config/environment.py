"""
Environment configuration management.

Handles switching between development and production environments.
"""

import os
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class Environment(str, Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class EnvironmentConfig(BaseModel):
    """Environment configuration settings."""
    
    model_config = ConfigDict(
        # Add any specific config here if needed
    )
    
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Current environment"
    )
    
    debug: bool = Field(
        default=True,
        description="Enable debug mode"
    )
    
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    @classmethod
    def from_env(cls) -> "EnvironmentConfig":
        """Create config from environment variables."""
        env_name = os.getenv("UNREALON_ENV", "development").lower()
        
        # Map environment names
        env_mapping = {
            "dev": Environment.DEVELOPMENT,
            "development": Environment.DEVELOPMENT,
            "prod": Environment.PRODUCTION,
            "production": Environment.PRODUCTION,
            "test": Environment.TESTING,
            "testing": Environment.TESTING,
        }
        
        environment = env_mapping.get(env_name, Environment.DEVELOPMENT)
        
        return cls(
            environment=environment,
            debug=environment != Environment.PRODUCTION,
            log_level=os.getenv("UNREALON_LOG_LEVEL", "DEBUG" if environment != Environment.PRODUCTION else "INFO")
        )
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == Environment.TESTING


# Global config instance
_environment_config: Optional[EnvironmentConfig] = None


def get_environment_config() -> EnvironmentConfig:
    """Get the global environment configuration."""
    global _environment_config
    
    if _environment_config is None:
        _environment_config = EnvironmentConfig.from_env()
    
    return _environment_config


def set_environment_config(config: EnvironmentConfig) -> None:
    """Set the global environment configuration."""
    global _environment_config
    _environment_config = config
