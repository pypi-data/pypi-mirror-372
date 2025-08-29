"""
Logging models - Phase 2 update.

Import from strictly typed websocket models to avoid duplication.
Following critical requirements - no raw Dict[str, Any].
"""

# Import strictly typed models from websocket package
from .websocket.logging import (
    LogEntryData,
    LogBatchData,
    LogContext
)

# Legacy compatibility
LogEntry = LogEntryData
LogQuery = LogContext
LogMetrics = LogBatchData

__all__ = [
    'LogEntryData',
    'LogBatchData',
    'LogContext',
    # Legacy names
    'LogEntry',
    'LogQuery',
    'LogMetrics'
]