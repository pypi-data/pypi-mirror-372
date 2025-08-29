"""Proxy exceptions - Phase 1 stubs."""
from .base import UnrealOnError, UnrealOnTimeoutError

class ProxyError(UnrealOnError):
    pass

class ProxyNotAvailableError(ProxyError):
    pass

class ProxyTimeoutError(UnrealOnTimeoutError):
    pass
