"""
Driver initialization logic.

Handles the setup and initialization of all driver components.
"""

import logging
from typing import List, TYPE_CHECKING

from ..core.config import DriverMode
from ..communication.websocket_client import WebSocketClient
from ..communication.session import DriverSession

if TYPE_CHECKING:
    from ..core.driver import UniversalDriver

logger = logging.getLogger(__name__)


class DriverInitializer:
    """Handles driver initialization process."""
    
    @staticmethod
    async def initialize_driver(driver: 'UniversalDriver', capabilities: List[str] = []) -> bool:
        """
        Initialize driver with all components.
        
        Args:
            driver: UniversalDriver instance
            capabilities: List of driver capabilities
            
        Returns:
            True if initialization successful
        """
        # Store capabilities
        driver.capabilities = capabilities
        
        try:
            logger.info(f"Initializing UniversalDriver: {driver.driver_id}")
            
            # Initialize manager system
            if not await driver.manager_registry.initialize_all():
                logger.error("Manager initialization failed")
                return False
            
            # Initialize module system
            await driver.module_registry.initialize_all()
            
            # Setup WebSocket and session
            await DriverInitializer._setup_communication(driver, capabilities)
            
            logger.info(f"UniversalDriver {driver.driver_id} initialized successfully")
            driver.is_initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Driver initialization failed: {e}")
            return False
    
    @staticmethod
    async def _setup_communication(driver: 'UniversalDriver', capabilities: List[str]):
        """Setup WebSocket client and session based on driver mode."""
        # Get WebSocket URL from config (auto-detected)
        websocket_url = driver.config.effective_websocket_url
        
        # Setup WebSocket client if URL available
        if websocket_url:
            driver.websocket_client = WebSocketClient(
                websocket_url,
                driver.driver_id
            )
            
            # Set WebSocket client for logger (always for logging)
            if driver.logger_manager:
                driver.logger_manager.websocket_client = driver.websocket_client
            
            # Only create RPC session in DAEMON mode
            if driver.config.mode == DriverMode.DAEMON:
                # Create session
                driver.session = DriverSession(
                    driver.driver_id,
                    driver.websocket_client
                )
                
                # Start session with capabilities
                if capabilities is not None:
                    if not await driver.session.start_session(capabilities):
                        logger.error("Session start failed")
                        raise RuntimeError("Session start failed")
            else:
                # In STANDALONE mode - try to connect WebSocket for logging (optional)
                try:
                    await driver.websocket_client.connect()
                    logger.info("WebSocket connected for logging only (standalone mode)")
                except Exception as e:
                    logger.warning(f"WebSocket connection failed in standalone mode (will use local logging): {e}")
                    # Continue without WebSocket - not critical in standalone mode
