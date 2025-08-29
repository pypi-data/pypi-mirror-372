"""
Communication exceptions for UnrealOn system.

Phase 1: Basic communication exceptions
"""

from .base import UnrealOnError, UnrealOnTimeoutError


class CommunicationError(UnrealOnError):
    """Base communication error."""
    pass


class WebSocketError(CommunicationError):
    """WebSocket communication error."""
    pass


class RPCError(CommunicationError):
    """RPC communication error."""
    pass
