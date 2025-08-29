"""
Validation exceptions for UnrealOn system.

Phase 1: Basic validation exceptions
"""

from .base import UnrealOnError, UnrealOnConfigurationError


class ValidationError(UnrealOnError):
    """Validation error for invalid data."""
    pass


class ConfigurationError(UnrealOnConfigurationError):
    """Configuration validation error."""
    pass
