"""
Communication layer.

WebSocket client and RPC session management.
"""

from .websocket_client import WebSocketClient
from .session import DriverSession

__all__ = ["WebSocketClient", "DriverSession"]
