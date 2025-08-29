"""
WebSocket Communication Models for UnrealOn RPC.

CRITICAL REQUIREMENTS COMPLIANT:
- No raw Dict[str, Any] usage
- 100% Pydantic v2 validation  
- Strict typing throughout
- Files under 500 lines

This file imports from strictly typed websocket models.
All raw dictionaries have been replaced with Pydantic models.

Phase 2: Core Systems - WebSocket Bridge
"""

# Import all strictly typed models from websocket package
from .websocket import *
from .websocket.logging import LogContext

# Export commonly used data models for easy access
__all__ = [
    # Message types and base
    'MessageType', 'WebSocketMessage',
    
    # Message classes
    'DriverRegistrationMessage', 'RegistrationResponseMessage',
    'TaskAssignmentMessage', 'TaskResultMessage', 
    'LogEntryMessage', 'LogBatchMessage',
    'HeartbeatMessage', 'ConfigurationUpdateMessage',
    'ErrorMessage', 'AckMessage',
    
    # Data models for strict typing
    'TaskAssignmentData', 'TaskResultData', 'TaskParameters',
    'DriverRegistrationData', 'HeartbeatData', 'LogEntryData', 'LogContext',
    
    # Utilities
    'create_error_message', 'create_ack_message',
    
]