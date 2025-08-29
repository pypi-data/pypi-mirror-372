"""
Health monitoring for driver components.

Provides health checks and status monitoring for the driver.
"""

import logging
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.driver import UniversalDriver

logger = logging.getLogger(__name__)


class HealthMonitor:
    """Monitors driver health and provides status information."""
    
    @staticmethod
    async def get_health_status(driver: 'UniversalDriver') -> Dict[str, Any]:
        """Get comprehensive health status."""
        try:
            # Get manager health
            manager_health = await driver.manager_registry.health_check_all()
            
            # Get module health
            module_health = await driver.module_registry.health_check_all()
            
            # Get session status
            session_status = None
            if driver.session:
                session_status = driver.session.get_status()
            
            return {
                "driver_id": driver.driver_id,
                "config": {
                    "mode": driver.config.mode.value,
                    "websocket_enabled": driver.config.websocket_url is not None
                },
                "managers": manager_health,
                "modules": module_health,
                "session": session_status
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "driver_id": driver.driver_id,
                "status": "error",
                "error": str(e)
            }
    
    @staticmethod
    def get_basic_status(driver: 'UniversalDriver') -> Dict[str, Any]:
        """Get basic driver status (synchronous)."""
        return {
            "driver_id": driver.driver_id,
            "is_initialized": driver.is_initialized,
            "is_daemon_mode": driver.session is not None,
            "is_connected": driver.websocket_client is not None and driver.websocket_client.is_connected,
            "manager_count": len(driver.manager_registry.managers) if driver.manager_registry else 0,
            "capabilities": driver.capabilities
        }
