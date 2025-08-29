"""
Driver WebSocket Models.

Strictly typed models for driver registration and responses.
No raw dictionaries - all data structures are Pydantic models.

Phase 2: Core Systems - WebSocket Bridge
"""

from typing import List, Optional
from pydantic import Field, ConfigDict, field_validator

from ..base import UnrealOnBaseModel
from .base import WebSocketMessage, MessageType
from ...version import get_driver_version


class DriverMetadata(UnrealOnBaseModel):
    """Driver metadata with strict typing."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    region: Optional[str] = Field(
        default=None,
        description="Driver deployment region"
    )
    
    environment: Optional[str] = Field(
        default="production",
        description="Environment (development, staging, production)"
    )
    
    max_concurrent_tasks: Optional[int] = Field(
        default=1,
        ge=1,
        le=100,
        description="Maximum concurrent tasks"
    )
    
    tags: List[str] = Field(
        default_factory=list,
        description="Driver tags for filtering"
    )


class DriverRegistrationData(UnrealOnBaseModel):
    """Driver registration data payload - strictly typed."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    driver_id: str = Field(
        min_length=1,
        max_length=100,
        description="Unique driver identifier"
    )
    
    driver_name: str = Field(
        min_length=1,
        max_length=200,
        description="Human-readable driver name"
    )
    
    driver_type: str = Field(
        min_length=1,
        max_length=50,
        description="Type of driver (universal, ecommerce, etc.)"
    )
    
    capabilities: List[str] = Field(
        default_factory=list,
        description="List of supported task types"
    )
    
    version: str = Field(
        default_factory=get_driver_version,
        pattern=r"^\d+\.\d+\.\d+$",
        description="Driver version (semver)"
    )
    
    metadata: DriverMetadata = Field(
        default_factory=DriverMetadata,
        description="Driver metadata"
    )
    
    @field_validator('capabilities')
    @classmethod
    def validate_capabilities(cls, v: List[str]) -> List[str]:
        """Validate capabilities list."""
        if not v:
            raise ValueError("Driver must have at least one capability")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_caps = []
        for cap in v:
            if cap not in seen:
                seen.add(cap)
                unique_caps.append(cap)
        
        return unique_caps


class DriverRegistrationMessage(WebSocketMessage):
    """Driver registration message (Driver → Server)."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    type: MessageType = Field(
        default=MessageType.DRIVER_REGISTER,
        frozen=True
    )
    
    data: DriverRegistrationData = Field(
        description="Driver registration data"
    )


class DriverConfiguration(UnrealOnBaseModel):
    """Driver configuration from server - strictly typed."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    heartbeat_interval: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Heartbeat interval in seconds"
    )
    
    log_level: str = Field(
        default="INFO",
        pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Logging level"
    )
    
    batch_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Log batch size"
    )
    
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum task retries"
    )
    
    timeout_seconds: int = Field(
        default=300,
        ge=30,
        le=3600,
        description="Default task timeout"
    )


class RegistrationResponseData(UnrealOnBaseModel):
    """Registration response data payload - strictly typed."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    success: bool = Field(
        description="Whether registration was successful"
    )
    
    driver_id: str = Field(
        description="Confirmed driver ID"
    )
    
    session_id: str = Field(
        description="WebSocket session ID"
    )
    
    message: str = Field(
        description="Registration status message"
    )
    
    configuration: DriverConfiguration = Field(
        default_factory=DriverConfiguration,
        description="Driver configuration from server"
    )


class RegistrationResponseMessage(WebSocketMessage):
    """Registration response message (Server → Driver)."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    type: MessageType = Field(
        default=MessageType.DRIVER_REGISTER_RESPONSE,
        frozen=True
    )
    
    data: RegistrationResponseData = Field(
        description="Registration response data"
    )
