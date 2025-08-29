"""Driver exceptions - Phase 1 stubs."""
from .base import UnrealOnError, UnrealOnTimeoutError

class DriverError(UnrealOnError):
    pass

class DriverNotFoundError(DriverError):
    pass

class DriverTimeoutError(UnrealOnTimeoutError):
    pass
