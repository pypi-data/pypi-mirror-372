"""
UniversalDriver - Clean, modular driver orchestrator.

The main driver class that coordinates all components through a clean,
organized architecture with separated concerns.
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable

from .config import DriverConfig
from ..communication.websocket_client import WebSocketClient
from ..communication.session import DriverSession
from ..factory.manager_factory import ManagerFactory
from ..lifecycle.initialization import DriverInitializer
from ..lifecycle.shutdown import DriverShutdown
from ..lifecycle.daemon import DaemonManager
from ..monitoring.health import HealthMonitor
from ..utilities.logging import LoggingUtility
from ..utilities.serialization import SerializationUtility

from ...managers import (
    LoggerManager, HttpManager, BrowserManager, CacheManager,
    ProxyManager, ThreadManager, UpdateManager, ManagerRegistry
)

from ...core_module import (
    EventManager,
    ModuleRegistry
)

from ...decorators import task, retry, schedule, timing

logger = logging.getLogger(__name__)


class UniversalDriver:
    """
    Universal Driver - Clean orchestrator for all parsing operations.
    
    Key Features:
    - Zero-config initialization with sensible defaults
    - Modular manager system (HTTP, Browser, Cache, etc.)
    - WebSocket communication for RPC and logging
    - Graceful shutdown with signal handling
    - Built-in utilities for common operations
    - Decorator-based task registration
    
    Usage:
        # Basic usage
        config = DriverConfig.for_development("my_parser")
        driver = UniversalDriver(config)
        await driver.initialize()
        
        # Daemon mode with RPC
        await driver.run_daemon_mode()
        
        # Standalone mode
        await driver.initialize()
        # ... your parsing logic
        await driver.shutdown()
    """
    
    def __init__(self, config: DriverConfig):
        """Initialize UniversalDriver with configuration."""
        self.config = config
        self.driver_id = config.name
        self.is_initialized = False
        self.capabilities: List[str] = []
        
        # Core components
        self.websocket_client: Optional[WebSocketClient] = None
        self.session: Optional[DriverSession] = None
        
        # Manager system (initialized by factory)
        self.manager_registry: Optional[ManagerRegistry] = None
        self.logger_manager: Optional[LoggerManager] = None
        self.http: Optional[HttpManager] = None
        self.browser: Optional[BrowserManager] = None
        self.cache: Optional[CacheManager] = None
        self.proxy: Optional[ProxyManager] = None
        self.threading: Optional[ThreadManager] = None
        self.update: Optional[UpdateManager] = None
        
        # Module system
        self.event_manager = EventManager()
        self.module_registry = ModuleRegistry(self.event_manager)
        
        # Utilities
        self._logging_util = LoggingUtility(self.driver_id)
        
        # Decorators (exposed as instance methods for convenience)
        self.task = task
        self.retry = retry
        self.schedule = schedule
        self.timing = timing
        
        # Setup managers using factory
        self._setup_components()
    
    def _setup_components(self):
        """Setup all driver components."""
        # Initialize managers using factory
        self.manager_registry = ManagerFactory.setup_managers(self)
        
        # Update logging utility with manager
        self._logging_util.logger_manager = self.logger_manager
        
        logger.debug(f"UniversalDriver components initialized: {self.driver_id}")
    
    # === Lifecycle Management ===
    
    async def initialize(self, capabilities: List[str] = []) -> bool:
        """
        Initialize driver with all components.
        
        Args:
            capabilities: List of driver capabilities
            
        Returns:
            True if initialization successful
        """
        return await DriverInitializer.initialize_driver(self, capabilities)
    
    async def shutdown(self):
        """Shutdown driver cleanly."""
        await DriverShutdown.shutdown_driver(self)
    
    async def run_daemon_mode(self, on_start_message: str = "Driver initialized, waiting for RPC tasks..."):
        """
        Run driver in daemon mode with graceful shutdown handling.
        
        Args:
            on_start_message: Message to display when daemon starts
        """
        await DaemonManager.run_daemon_mode(self, on_start_message)
    
    # === Task Registration ===
    
    def register_task_handler(self, task_type: str, handler: Callable):
        """Register task handler for RPC tasks."""
        if self.session:
            self.session.register_task_handler(task_type, handler)
        else:
            logger.warning("No session available for task handler registration")
    
    # === Health & Monitoring ===
    
    async def health_check(self) -> Dict[str, Any]:
        """Get comprehensive health status."""
        return await HealthMonitor.get_health_status(self)
    
    def get_status(self) -> Dict[str, Any]:
        """Get basic driver status (synchronous)."""
        return HealthMonitor.get_basic_status(self)
    
    # === Utilities ===
    
    def save_results_to_file(self, data: dict, filename: str, results_dir: Optional[str] = None) -> Path:
        """
        Save parsing results to JSON file with automatic serialization.
        
        Args:
            data: Data to save (can contain Pydantic models)
            filename: Base filename (without extension)
            results_dir: Directory to save to (default: ./data/results)
            
        Returns:
            Path to saved file
        """
        return SerializationUtility.save_results_to_file(data, filename, results_dir)
    
    # === Logging Methods ===
    
    def log(self, level: str, message: str, context: Optional[Dict[str, Any]] = None):
        """Log message through logger manager."""
        self._logging_util.log(level, message, context)
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log debug message."""
        self._logging_util.debug(message, context)
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log info message."""
        self._logging_util.info(message, context)
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log warning message."""
        self._logging_util.warning(message, context)
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log error message."""
        self._logging_util.error(message, context)
    
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log critical message."""
        self._logging_util.critical(message, context)
    
    # === Convenience Properties ===
    
    @property
    def is_daemon_mode(self) -> bool:
        """Check if driver is running in daemon mode."""
        return self.session is not None
    
    @property
    def is_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self.websocket_client is not None and self.websocket_client.is_connected
    
    @property
    def manager_count(self) -> int:
        """Get number of active managers."""
        return len(self.manager_registry.managers) if self.manager_registry else 0
    
    def __repr__(self) -> str:
        """String representation of driver."""
        status = "initialized" if self.is_initialized else "not initialized"
        mode = "daemon" if self.is_daemon_mode else "standalone"
        return f"UniversalDriver(id='{self.driver_id}', status='{status}', mode='{mode}')"
