"""
Daemon mode management.

Handles running the driver in daemon mode with graceful shutdown.
"""

import asyncio
import logging
import signal
import sys
from typing import TYPE_CHECKING

from .initialization import DriverInitializer
from .shutdown import DriverShutdown

if TYPE_CHECKING:
    from ..core.driver import UniversalDriver

logger = logging.getLogger(__name__)


class DaemonManager:
    """Manages daemon mode operations."""
    
    @staticmethod
    async def run_daemon_mode(driver: 'UniversalDriver', on_start_message: str = "Driver initialized, waiting for RPC tasks..."):
        """
        Run driver in daemon mode with graceful shutdown handling.
        
        Args:
            driver: UniversalDriver instance
            on_start_message: Message to display when daemon starts
        """
        # Flag for graceful shutdown
        shutdown_event = asyncio.Event()
        
        def signal_handler():
            """Handle shutdown signals gracefully."""
            logger.info("Shutdown signal received")
            shutdown_event.set()
        
        # Register signal handlers
        if sys.platform != "win32":
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(sig, signal_handler)
        
        try:
            # Initialize driver with capabilities
            success = await DriverInitializer.initialize_driver(driver, driver.capabilities)
            if not success:
                raise RuntimeError("Driver initialization failed")
            
            # Call on_start hook if available
            if hasattr(driver, 'on_start') and callable(driver.on_start):
                await driver.on_start()
            
            logger.info(on_start_message)
            
            # Keep running until shutdown signal
            await shutdown_event.wait()
            
        except Exception as e:
            logger.error(f"Daemon mode error: {e}")
            raise
        finally:
            # Always shutdown cleanly
            try:
                # Call on_shutdown hook if available
                if hasattr(driver, 'on_shutdown') and callable(driver.on_shutdown):
                    await driver.on_shutdown()
                
                await DriverShutdown.shutdown_driver(driver)
                logger.info("Driver shutdown complete")
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")
