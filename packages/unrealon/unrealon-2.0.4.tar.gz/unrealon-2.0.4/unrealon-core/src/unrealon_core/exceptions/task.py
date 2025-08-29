"""Task exceptions - Phase 1 stubs."""
from .base import UnrealOnError, UnrealOnTimeoutError
from .validation import ValidationError

class TaskError(UnrealOnError):
    pass

class TaskTimeoutError(UnrealOnTimeoutError):
    pass

class TaskValidationError(ValidationError):
    pass
