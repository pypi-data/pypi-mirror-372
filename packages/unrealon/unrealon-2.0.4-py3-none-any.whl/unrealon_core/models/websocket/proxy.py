"""
Proxy WebSocket Models.

All proxy-related models for WebSocket communication between Driver and RPC.
Includes core proxy models and WebSocket message wrappers.

Phase 3.4: Proxy System - WebSocket Integration
Following critical requirements: <500 lines, functions <20 lines, Pydantic v2 only
"""

from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import Field, ConfigDict, field_validator

from ..base import UnrealOnBaseModel, TimestampedModel, IdentifiedModel
from .base import WebSocketMessage, MessageType


# Core Proxy Models

class ProxyType(str, Enum):
    """Proxy connection types."""
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


class ProxyHealthStatus(str, Enum):
    """Proxy health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ProxyCredentials(UnrealOnBaseModel):
    """Proxy authentication credentials."""
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=200)


class ProxyInfo(IdentifiedModel):
    """Core proxy information for WebSocket communication."""
    host: str = Field(..., min_length=1, max_length=255)
    port: int = Field(..., ge=1, le=65535)
    proxy_type: ProxyType = ProxyType.HTTP
    credentials: Optional[ProxyCredentials] = None
    
    # Metadata
    country_code: Optional[str] = Field(None, min_length=2, max_length=2)
    city: Optional[str] = Field(None, max_length=100)
    provider: Optional[str] = Field(None, max_length=100)
    
    @field_validator('host')
    @classmethod
    def validate_host(cls, v: str) -> str:
        """Validate host format."""
        if not v or v.isspace():
            raise ValueError("Host cannot be empty")
        return v.strip()
    
    @field_validator('country_code')
    @classmethod
    def validate_country_code(cls, v: Optional[str]) -> Optional[str]:
        """Validate ISO country code format."""
        if v is None:
            return v
        return v.upper() if len(v) == 2 else v
    
    def get_url(self) -> str:
        """Get proxy URL for HTTP requests."""
        if self.credentials:
            return f"{self.proxy_type}://{self.credentials.username}:{self.credentials.password}@{self.host}:{self.port}"
        return f"{self.proxy_type}://{self.host}:{self.port}"


class ProxyAssignment(TimestampedModel):
    """Proxy assignment for WebSocket communication."""
    assignment_id: str = Field(..., min_length=1)
    task_id: str = Field(..., min_length=1)
    proxy: ProxyInfo
    
    # Assignment details
    expires_at: Optional[datetime] = None
    pool_id: str = Field(..., min_length=1)
    max_requests: Optional[int] = Field(None, ge=1)
    current_requests: int = Field(default=0, ge=0)


# WebSocket Data Payloads

class ProxyRequestData(UnrealOnBaseModel):
    """Proxy request data payload - strictly typed."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    task_id: str = Field(
        min_length=1,
        max_length=100,
        description="Task identifier requesting proxy"
    )
    
    task_type: str = Field(
        min_length=1,
        max_length=50,
        description="Type of task needing proxy"
    )
    
    # Requirements
    required_country: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=2,
        description="Required country code (ISO 2-letter)"
    )
    
    required_proxy_type: Optional[ProxyType] = Field(
        default=None,
        description="Required proxy type"
    )
    
    pool_preference: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Preferred proxy pool name"
    )
    
    # Context
    target_domain: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Target domain for proxy selection"
    )
    
    priority: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Request priority (1=low, 10=high)"
    )
    
    exclude_proxy_ids: List[str] = Field(
        default_factory=list,
        description="Proxy IDs to exclude from selection"
    )


class ProxyResponseData(UnrealOnBaseModel):
    """Proxy response data payload - strictly typed."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    success: bool = Field(
        description="Whether proxy assignment was successful"
    )
    
    assignment: Optional[ProxyAssignment] = Field(
        default=None,
        description="Proxy assignment details (if successful)"
    )
    
    error_message: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Error message (if failed)"
    )
    
    error_code: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Error code (if failed)"
    )
    
    retry_after_seconds: Optional[int] = Field(
        default=None,
        ge=1,
        le=3600,
        description="Seconds to wait before retry (if applicable)"
    )
    
    available_pools: List[str] = Field(
        default_factory=list,
        description="Available proxy pools for this request"
    )


class ProxyHealthReportData(UnrealOnBaseModel):
    """Proxy health report data payload - strictly typed."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    assignment_id: str = Field(
        min_length=1,
        description="Assignment ID for the proxy"
    )
    
    proxy_id: str = Field(
        min_length=1,
        description="Proxy identifier"
    )
    
    task_id: str = Field(
        min_length=1,
        description="Task that used the proxy"
    )
    
    # Health status
    status: ProxyHealthStatus = Field(
        description="Current proxy health status"
    )
    
    response_time_ms: Optional[float] = Field(
        default=None,
        ge=0,
        description="Response time in milliseconds"
    )
    
    success: bool = Field(
        description="Whether the proxy request was successful"
    )
    
    # Error details (if failed)
    error_type: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Error type (if failed)"
    )
    
    error_message: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Error message (if failed)"
    )
    
    http_status_code: Optional[int] = Field(
        default=None,
        ge=100,
        le=599,
        description="HTTP status code (if applicable)"
    )
    
    target_url: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Target URL that was accessed"
    )


class ProxyRotationRequestData(UnrealOnBaseModel):
    """Proxy rotation request data payload - strictly typed."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    current_assignment_id: str = Field(
        min_length=1,
        description="Current proxy assignment ID"
    )
    
    reason: str = Field(
        min_length=1,
        max_length=200,
        description="Reason for rotation request"
    )
    
    # New requirements
    new_country_preference: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=2,
        description="New country preference (if any)"
    )
    
    exclude_proxy_ids: List[str] = Field(
        default_factory=list,
        description="Proxy IDs to exclude from new selection"
    )
    
    urgent: bool = Field(
        default=False,
        description="Whether this is an urgent rotation request"
    )


class ProxyReleaseData(UnrealOnBaseModel):
    """Proxy release data payload - strictly typed."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    assignment_id: str = Field(
        min_length=1,
        description="Assignment ID to release"
    )
    
    task_id: str = Field(
        min_length=1,
        description="Task that was using the proxy"
    )
    
    reason: str = Field(
        default="task_completed",
        max_length=100,
        description="Reason for release"
    )
    
    # Usage statistics
    requests_made: int = Field(
        default=0,
        ge=0,
        description="Number of requests made with this proxy"
    )
    
    bytes_transferred: int = Field(
        default=0,
        ge=0,
        description="Total bytes transferred"
    )
    
    session_duration_seconds: float = Field(
        default=0.0,
        ge=0,
        description="Total session duration in seconds"
    )


# WebSocket Messages

class ProxyRequestMessage(WebSocketMessage):
    """Proxy request message (Driver → Server)."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    type: MessageType = Field(
        default=MessageType.PROXY_REQUEST,
        frozen=True
    )
    
    data: ProxyRequestData = Field(
        description="Proxy request data"
    )


class ProxyResponseMessage(WebSocketMessage):
    """Proxy response message (Server → Driver)."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    type: MessageType = Field(
        default=MessageType.PROXY_RESPONSE,
        frozen=True
    )
    
    data: ProxyResponseData = Field(
        description="Proxy response data"
    )


class ProxyHealthReportMessage(WebSocketMessage):
    """Proxy health report message (Driver → Server)."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    type: MessageType = Field(
        default=MessageType.PROXY_HEALTH_REPORT,
        frozen=True
    )
    
    data: ProxyHealthReportData = Field(
        description="Proxy health report data"
    )


class ProxyRotationRequestMessage(WebSocketMessage):
    """Proxy rotation request message (Driver → Server)."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    type: MessageType = Field(
        default=MessageType.PROXY_ROTATION_REQUEST,
        frozen=True
    )
    
    data: ProxyRotationRequestData = Field(
        description="Proxy rotation request data"
    )


class ProxyReleaseMessage(WebSocketMessage):
    """Proxy release message (Driver → Server)."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    type: MessageType = Field(
        default=MessageType.PROXY_RELEASE,
        frozen=True
    )
    
    data: ProxyReleaseData = Field(
        description="Proxy release data"
    )


# ===== UTILITY MODELS =====


class ProxyHealthRecord(UnrealOnBaseModel):
    """Proxy health tracking record."""
    
    status: ProxyHealthStatus = Field(
        description="Current health status"
    )
    response_time_ms: Optional[int] = Field(
        default=None,
        ge=0,
        description="Response time in milliseconds"
    )
    success: bool = Field(
        description="Whether last operation was successful"
    )
    last_update: datetime = Field(
        description="Last update timestamp"
    )
    error_type: Optional[str] = Field(
        default=None,
        description="Error type if any"
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if any"
    )


class ProxyManagerStats(UnrealOnBaseModel):
    """Proxy distribution manager statistics."""
    
    total_requests: int = Field(
        default=0,
        ge=0,
        description="Total proxy requests"
    )
    successful_assignments: int = Field(
        default=0,
        ge=0,
        description="Successful assignments"
    )
    failed_assignments: int = Field(
        default=0,
        ge=0,
        description="Failed assignments"
    )
    health_reports: int = Field(
        default=0,
        ge=0,
        description="Health reports received"
    )
    active_assignments: int = Field(
        default=0,
        ge=0,
        description="Currently active assignments"
    )
    tracked_health_records: int = Field(
        default=0,
        ge=0,
        description="Health records being tracked"
    )
