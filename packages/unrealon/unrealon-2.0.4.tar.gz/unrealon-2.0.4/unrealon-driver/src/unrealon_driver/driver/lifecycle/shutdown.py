"""
Driver shutdown logic.

Handles clean shutdown of all driver components.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.driver import UniversalDriver

logger = logging.getLogger(__name__)


class DriverShutdown:
    """Handles driver shutdown process."""
    
    @staticmethod
    async def shutdown_driver(driver: 'UniversalDriver'):
        """Shutdown driver cleanly."""
        try:
            logger.info(f"Shutting down UniversalDriver: {driver.driver_id}")
            
            # Stop session
            if driver.session:
                await driver.session.stop_session()
            
            # Disconnect WebSocket client
            if driver.websocket_client:
                await driver.websocket_client.disconnect()
            
            # Stop event manager
            await driver.event_manager.stop()
            
            # Stop module system
            await driver.module_registry.stop_all()
            
            # Shutdown managers
            await driver.manager_registry.shutdown_all()
            
            logger.info(f"UniversalDriver {driver.driver_id} shutdown complete")
            driver.is_initialized = False
            
        except Exception as e:
            logger.error(f"Driver shutdown error: {e}")
            # Still mark as not initialized even if shutdown failed
            driver.is_initialized = False
