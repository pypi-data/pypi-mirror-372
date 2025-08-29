"""
Driver models - Phase 2 update.

Import from strictly typed websocket models to avoid duplication.
Following critical requirements - no raw Dict[str, Any].
"""

# Import strictly typed models from websocket package
from .websocket.driver import (
    DriverRegistrationData,
    DriverMetadata,
    DriverConfiguration,
    RegistrationResponseData
)

# Legacy compatibility
DriverInfo = DriverRegistrationData
DriverConfig = DriverConfiguration
DriverCapability = DriverMetadata

__all__ = [
    'DriverRegistrationData',
    'DriverMetadata', 
    'DriverConfiguration',
    'RegistrationResponseData',
    # Legacy names
    'DriverInfo',
    'DriverConfig',
    'DriverCapability'
]