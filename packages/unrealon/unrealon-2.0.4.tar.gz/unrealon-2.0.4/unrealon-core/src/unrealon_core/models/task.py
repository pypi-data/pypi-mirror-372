"""
Task models - Phase 2 update.

Import from strictly typed websocket models to avoid duplication.
Following critical requirements - no raw Dict[str, Any].
"""

# Import strictly typed models from websocket package
from .websocket.tasks import (
    TaskAssignmentData,
    TaskResultData,
    TaskParameters,
    TaskMetadata
)

__all__ = [
    'TaskAssignmentData',
    'TaskResultData',
    'TaskParameters',
    'TaskMetadata',
]