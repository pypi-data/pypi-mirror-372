"""
Base Pydantic models for UnrealOn system.

These models provide common functionality and validation patterns
used throughout the system. Built with Pydantic v2 for maximum
performance and type safety.

Phase 1: Bedrock Foundation - These models are the foundation
for all other models in the system.
"""

from datetime import datetime
from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict, field_validator
import uuid

from ..utils.time import utc_now


class UnrealOnBaseModel(BaseModel):
    """
    Base model for all UnrealOn models.
    
    Provides:
    - Strict validation (no extra fields)
    - JSON serialization/deserialization
    - Type safety with Pydantic v2
    - Common utility methods
    """
    
    model_config = ConfigDict(
        # Pydantic v2 configuration for maximum strictness
        str_strip_whitespace=True,      # Auto-strip whitespace
        validate_assignment=True,       # Validate on assignment
        use_enum_values=True,          # Use enum values in serialization
        extra='forbid',                # Strict - no extra fields allowed
        frozen=False,                  # Allow mutation by default
        arbitrary_types_allowed=True,  # Allow custom types
        validate_default=True,         # Validate default values
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for JSON serialization."""
        return self.model_dump(mode='json', exclude_none=True)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create instance from dictionary."""
        return cls.model_validate(data)
    
    def to_json(self) -> str:
        """Convert model to JSON string."""
        return self.model_dump_json(exclude_none=True)
    
    @classmethod
    def from_json(cls, json_str: str):
        """Create instance from JSON string."""
        return cls.model_validate_json(json_str)
    
    def update_from_dict(self, data: Dict[str, Any]) -> 'UnrealOnBaseModel':
        """Update model fields from dictionary."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self
    
    def copy_with_updates(self, **updates) -> 'UnrealOnBaseModel':
        """Create a copy with updated fields."""
        return self.model_copy(update=updates)


class TimestampedModel(UnrealOnBaseModel):
    """
    Base model with automatic timestamp fields.
    
    Provides:
    - created_at: Auto-set on creation
    - updated_at: Manual update via touch()
    - age_seconds: Calculated property
    """
    
    created_at: datetime = Field(
        default_factory=utc_now,
        description="Timestamp when the model was created"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the model was last updated"
    )
    
    def touch(self) -> 'TimestampedModel':
        """Update the updated_at timestamp."""
        self.updated_at = utc_now()
        return self
    
    @property
    def age_seconds(self) -> float:
        """Get age of the model in seconds."""
        return (utc_now() - self.created_at).total_seconds()
    
    @property
    def last_modified_seconds(self) -> float:
        """Get seconds since last modification."""
        reference_time = self.updated_at or self.created_at
        return (utc_now() - reference_time).total_seconds()


class IdentifiedModel(UnrealOnBaseModel):
    """
    Base model with unique ID field.
    
    Provides:
    - id: UUID4 string by default
    - String representation
    - Equality comparison by ID
    """
    
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the model",
        min_length=1
    )
    
    @field_validator('id')
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate ID is not empty."""
        if not v or not v.strip():
            raise ValueError("ID cannot be empty")
        return v.strip()
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id='{self.id}')"
    
    def __eq__(self, other) -> bool:
        """Compare models by ID."""
        if not isinstance(other, IdentifiedModel):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash by ID for use in sets/dicts."""
        return hash(self.id)


class StatusModel(UnrealOnBaseModel):
    """
    Base model with status tracking.
    
    Provides:
    - status: Current status string
    - status_message: Optional status description
    - status_updated_at: Timestamp of last status change
    - Status update methods
    """
    
    status: str = Field(
        description="Current status of the model",
        min_length=1
    )
    status_message: Optional[str] = Field(
        default=None,
        description="Optional message describing the status"
    )
    status_updated_at: datetime = Field(
        default_factory=utc_now,
        description="Timestamp when status was last updated"
    )
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status is not empty."""
        if not v or not v.strip():
            raise ValueError("Status cannot be empty")
        return v.strip()
    
    def update_status(self, status: str, message: Optional[str] = None) -> 'StatusModel':
        """Update status with timestamp and optional message."""
        self.status = status
        self.status_message = message
        self.status_updated_at = utc_now()
        return self
    
    @property
    def status_age_seconds(self) -> float:
        """Get age of current status in seconds."""
        return (utc_now() - self.status_updated_at).total_seconds()
    
    def is_status(self, *statuses: str) -> bool:
        """Check if current status matches any of the provided statuses."""
        return self.status in statuses


class MetadataModel(UnrealOnBaseModel):
    """
    Base model with metadata field.
    
    Provides:
    - metadata: Dictionary for arbitrary key-value data
    - Helper methods for metadata manipulation
    """
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary metadata key-value pairs"
    )
    
    def set_metadata(self, key: str, value: Any) -> 'MetadataModel':
        """Set metadata value."""
        self.metadata[key] = value
        return self
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value with optional default."""
        return self.metadata.get(key, default)
    
    def has_metadata(self, key: str) -> bool:
        """Check if metadata key exists."""
        return key in self.metadata
    
    def remove_metadata(self, key: str) -> 'MetadataModel':
        """Remove metadata key if it exists."""
        self.metadata.pop(key, None)
        return self
    
    def clear_metadata(self) -> 'MetadataModel':
        """Clear all metadata."""
        self.metadata.clear()
        return self
    
    def update_metadata(self, **updates) -> 'MetadataModel':
        """Update metadata with multiple key-value pairs."""
        self.metadata.update(updates)
        return self


# Combined base models for common use cases
class FullBaseModel(IdentifiedModel, TimestampedModel, StatusModel, MetadataModel):
    """
    Complete base model with ID, timestamps, status, and metadata.
    
    Use this for complex entities that need full tracking:
    - Drivers
    - Tasks
    - Complex configurations
    """
    pass


class SimpleBaseModel(IdentifiedModel, TimestampedModel):
    """
    Simple base model with ID and timestamps only.
    
    Use this for simple entities:
    - Messages
    - Simple configurations
    - Temporary objects
    """
    pass


class ConfigBaseModel(UnrealOnBaseModel):
    """
    Base model for configuration objects.
    
    Provides validation for configuration models
    without unnecessary fields like timestamps.
    """
    
    def validate_config(self) -> bool:
        """Override in subclasses to add custom validation."""
        return True
    
    def merge_with(self, other: 'ConfigBaseModel') -> 'ConfigBaseModel':
        """Merge this config with another, other takes precedence."""
        if not isinstance(other, self.__class__):
            raise ValueError(f"Cannot merge {self.__class__} with {other.__class__}")
        
        # Get all fields from both models
        self_dict = self.model_dump()
        other_dict = other.model_dump()
        
        # Merge dictionaries (other takes precedence)
        merged = {**self_dict, **other_dict}
        
        # Create new instance
        return self.__class__.model_validate(merged)
