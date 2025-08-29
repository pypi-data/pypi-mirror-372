"""
Task WebSocket Models.

Strictly typed models for task assignments and results.
No raw dictionaries - all data structures are Pydantic models.

Phase 2: Core Systems - WebSocket Bridge
"""

from typing import Optional, List, Union
from pydantic import Field, ConfigDict, field_validator, HttpUrl

from ..base import UnrealOnBaseModel
from .base import WebSocketMessage, MessageType


class TaskParameters(UnrealOnBaseModel):
    """Task-specific parameters - strictly typed."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    selectors: Optional[List[str]] = Field(
        default=None,
        description="CSS selectors for parsing"
    )
    
    wait_for: Optional[str] = Field(
        default=None,
        description="Element to wait for before parsing"
    )
    
    scroll_to_bottom: bool = Field(
        default=False,
        description="Whether to scroll to bottom"
    )
    
    screenshot: bool = Field(
        default=False,
        description="Whether to take screenshot"
    )
    
    user_agent: Optional[str] = Field(
        default=None,
        description="Custom user agent"
    )
    
    headers: Optional[List[str]] = Field(
        default=None,
        description="Custom headers as key:value pairs"
    )


class TaskMetadata(UnrealOnBaseModel):
    """Task metadata - strictly typed."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    source: Optional[str] = Field(
        default=None,
        description="Task source system"
    )
    
    batch_id: Optional[str] = Field(
        default=None,
        description="Batch identifier"
    )
    
    user_id: Optional[str] = Field(
        default=None,
        description="User who created the task"
    )
    
    tags: List[str] = Field(
        default_factory=list,
        description="Task tags"
    )


class TaskAssignmentData(UnrealOnBaseModel):
    """Task assignment data payload - strictly typed."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    task_id: str = Field(
        min_length=1,
        description="Unique task identifier"
    )
    
    task_type: str = Field(
        min_length=1,
        description="Type of task to execute"
    )
    
    url: HttpUrl = Field(
        description="Target URL for the task"
    )
    
    parameters: TaskParameters = Field(
        default_factory=TaskParameters,
        description="Task-specific parameters"
    )
    
    priority: str = Field(
        default="normal",
        pattern=r"^(low|normal|high|urgent|critical)$",
        description="Task priority level"
    )
    
    timeout_seconds: float = Field(
        default=300.0,
        ge=30.0,
        le=3600.0,
        description="Task timeout in seconds"
    )
    
    retry_count: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Number of retries allowed"
    )
    
    metadata: TaskMetadata = Field(
        default_factory=TaskMetadata,
        description="Additional task metadata"
    )


class TaskAssignmentMessage(WebSocketMessage):
    """Task assignment message (Server → Driver)."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    type: MessageType = Field(
        default=MessageType.TASK_ASSIGN,
        frozen=True
    )
    
    data: TaskAssignmentData = Field(
        description="Task assignment data"
    )


class TaskResultData(UnrealOnBaseModel):
    """Task result data - strictly typed."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    # Basic fields
    title: Optional[str] = Field(
        default=None,
        description="Extracted title"
    )
    
    description: Optional[str] = Field(
        default=None,
        description="Extracted description"
    )
    
    price: Optional[str] = Field(
        default=None,
        description="Extracted price"
    )
    
    images: List[str] = Field(
        default_factory=list,
        description="Extracted image URLs"
    )
    
    links: List[str] = Field(
        default_factory=list,
        description="Extracted links"
    )
    
    # Custom fields for specific parsers
    custom_fields: List[str] = Field(
        default_factory=list,
        description="Custom extracted fields as key:value pairs"
    )


class TaskResultPayload(UnrealOnBaseModel):
    """Task result payload - strictly typed."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    task_id: str = Field(
        description="Task identifier"
    )
    
    status: str = Field(
        pattern=r"^(completed|failed|timeout|cancelled)$",
        description="Task completion status"
    )
    
    result: Optional[TaskResultData] = Field(
        default=None,
        description="Task result data (if successful)"
    )
    
    error_message: Optional[str] = Field(
        default=None,
        description="Error message (if failed)"
    )
    
    error_code: Optional[str] = Field(
        default=None,
        description="Error code (if failed)"
    )
    
    execution_time_seconds: float = Field(
        default=0.0,
        ge=0.0,
        description="Task execution time in seconds"
    )
    
    screenshot_url: Optional[str] = Field(
        default=None,
        description="Screenshot URL (if taken)"
    )
    
    metadata: TaskMetadata = Field(
        default_factory=TaskMetadata,
        description="Additional result metadata"
    )
    
    @field_validator('result')
    @classmethod
    def validate_result(cls, v: Optional[TaskResultData], info) -> Optional[TaskResultData]:
        """Validate result based on status."""
        status = info.data.get('status')
        
        if status == 'completed' and v is None:
            raise ValueError("Result is required for completed tasks")
        
        if status != 'completed' and v is not None:
            raise ValueError("Result should be None for non-completed tasks")
        
        return v


class TaskResultMessage(WebSocketMessage):
    """Task result message (Driver → Server)."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    type: MessageType = Field(
        default=MessageType.TASK_RESULT,
        frozen=True
    )
    
    data: TaskResultPayload = Field(
        description="Task result data"
    )
