"""
WebSocket Models Package.

Strictly typed WebSocket communication models following critical requirements:
- No raw Dict[str, Any] usage
- 100% Pydantic v2 validation
- Files under 500 lines each
- Complete type safety

Phase 2: Core Systems - WebSocket Bridge
"""

from .base import MessageType, WebSocketMessage
from .driver import (
    DriverRegistrationData, DriverRegistrationMessage,
    RegistrationResponseData, RegistrationResponseMessage
)
from .tasks import (
    TaskAssignmentData, TaskAssignmentMessage,
    TaskResultData, TaskResultMessage
)
from .logging import (
    LogEntryData, LogEntryMessage,
    LogBatchData, LogBatchMessage
)
from .heartbeat import HeartbeatData, HeartbeatMessage
from .config import ConfigurationUpdateData, ConfigurationUpdateMessage
from .errors import ErrorData, ErrorMessage, AckData, AckMessage
from .proxy import (
    # Core models
    ProxyType, ProxyHealthStatus, ProxyCredentials, ProxyInfo, ProxyAssignment,
    # Data payloads
    ProxyRequestData, ProxyResponseData, ProxyHealthReportData,
    ProxyRotationRequestData, ProxyReleaseData,
    # WebSocket messages
    ProxyRequestMessage, ProxyResponseMessage, ProxyHealthReportMessage,
    ProxyRotationRequestMessage, ProxyReleaseMessage
)

from .utils import create_error_message, create_ack_message

__all__ = [
    # Base
    'MessageType',
    'WebSocketMessage',
    
    # Driver messages
    'DriverRegistrationData',
    'DriverRegistrationMessage', 
    'RegistrationResponseData',
    'RegistrationResponseMessage',
    
    # Task messages
    'TaskAssignmentData',
    'TaskAssignmentMessage',
    'TaskResultData', 
    'TaskResultMessage',
    
    # Logging messages
    'LogEntryData',
    'LogEntryMessage',
    'LogBatchData',
    'LogBatchMessage',
    
    # Heartbeat messages
    'HeartbeatData',
    'HeartbeatMessage',
    
    # Configuration messages
    'ConfigurationUpdateData',
    'ConfigurationUpdateMessage',
    
    # Error messages
    'ErrorData',
    'ErrorMessage',
    'AckData',
    'AckMessage',
    
    # Proxy core models
    'ProxyType', 'ProxyHealthStatus', 'ProxyCredentials', 'ProxyInfo', 'ProxyAssignment',
    # Proxy data payloads
    'ProxyRequestData', 'ProxyResponseData', 'ProxyHealthReportData',
    'ProxyRotationRequestData', 'ProxyReleaseData',
    # Proxy messages
    'ProxyRequestMessage', 'ProxyResponseMessage', 'ProxyHealthReportMessage',
    'ProxyRotationRequestMessage', 'ProxyReleaseMessage',
    
    # Utilities
    'create_error_message',
    'create_ack_message'
]
