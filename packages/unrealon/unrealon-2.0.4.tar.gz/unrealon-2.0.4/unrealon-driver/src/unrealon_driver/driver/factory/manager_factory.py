"""
Manager Factory - Setup and configuration of all managers.

Handles the creation and configuration of manager components.
"""

import logging
from typing import TYPE_CHECKING

from ...managers import (
    LoggerManager, HttpManager, BrowserManager, CacheManager,
    ProxyManager, ThreadManager, UpdateManager, ManagerRegistry
)
from ...managers.logger import LoggerManagerConfig
from ...managers.http import HttpManagerConfig
from ...managers.browser import BrowserManagerConfig
from ...managers.cache import CacheManagerConfig
from ...managers.proxy import ProxyManagerConfig
from ...managers.threading import ThreadManagerConfig
from ...managers.update import UpdateManagerConfig

if TYPE_CHECKING:
    from ..core.driver import UniversalDriver

logger = logging.getLogger(__name__)


class ManagerFactory:
    """Factory for creating and configuring manager components."""
    
    @staticmethod
    def setup_managers(driver: 'UniversalDriver') -> ManagerRegistry:
        """
        Setup all managers with configurations.
        
        Args:
            driver: UniversalDriver instance
            
        Returns:
            Configured ManagerRegistry
        """
        # Create registry
        manager_registry = ManagerRegistry()
        
        # Setup each manager
        ManagerFactory._setup_logger_manager(driver, manager_registry)
        ManagerFactory._setup_http_manager(driver, manager_registry)
        ManagerFactory._setup_browser_manager(driver, manager_registry)
        ManagerFactory._setup_cache_manager(driver, manager_registry)
        ManagerFactory._setup_proxy_manager(driver, manager_registry)
        ManagerFactory._setup_threading_manager(driver, manager_registry)
        ManagerFactory._setup_update_manager(driver, manager_registry)
        
        logger.debug(f"Managers setup complete for driver: {driver.driver_id}")
        return manager_registry
    
    @staticmethod
    def _setup_logger_manager(driver: 'UniversalDriver', registry: ManagerRegistry):
        """Setup logger manager."""
        logger_config = LoggerManagerConfig(
            enabled=True,
            log_file=driver.config.log_file,
            log_level=driver.config.log_level,
            driver_id=driver.driver_id,
            timeout=driver.config.websocket_timeout
        )
        driver.logger_manager = LoggerManager(logger_config)
        registry.register(driver.logger_manager)
    
    @staticmethod
    def _setup_http_manager(driver: 'UniversalDriver', registry: ManagerRegistry):
        """Setup HTTP manager."""
        http_config = HttpManagerConfig(
            enabled=True,
            timeout=driver.config.http_timeout,
            max_retries=driver.config.max_retries
        )
        driver.http = HttpManager(http_config)
        registry.register(driver.http)
    
    @staticmethod
    def _setup_browser_manager(driver: 'UniversalDriver', registry: ManagerRegistry):
        """Setup browser manager."""
        browser_config = BrowserManagerConfig(
            enabled=True,
            headless=driver.config.browser_headless,
            timeout=driver.config.browser_timeout,
            parser_name=driver.driver_id
        )
        driver.browser = BrowserManager(browser_config)
        registry.register(driver.browser)
    
    @staticmethod
    def _setup_cache_manager(driver: 'UniversalDriver', registry: ManagerRegistry):
        """Setup cache manager."""
        cache_config = CacheManagerConfig(
            enabled=driver.config.cache_enabled,
            default_ttl=driver.config.cache_ttl
        )
        driver.cache = CacheManager(cache_config)
        registry.register(driver.cache)
    
    @staticmethod
    def _setup_proxy_manager(driver: 'UniversalDriver', registry: ManagerRegistry):
        """Setup proxy manager."""
        proxy_config = ProxyManagerConfig(
            enabled=driver.config.proxy_enabled,
            rotation_interval=driver.config.proxy_rotation_interval
        )
        driver.proxy = ProxyManager(proxy_config)
        registry.register(driver.proxy)
    
    @staticmethod
    def _setup_threading_manager(driver: 'UniversalDriver', registry: ManagerRegistry):
        """Setup threading manager."""
        threading_config = ThreadManagerConfig(
            enabled=True,
            max_workers=driver.config.max_workers
        )
        driver.threading = ThreadManager(threading_config)
        registry.register(driver.threading)
    
    @staticmethod
    def _setup_update_manager(driver: 'UniversalDriver', registry: ManagerRegistry):
        """Setup update manager."""
        update_config = UpdateManagerConfig(
            enabled=True
        )
        driver.update = UpdateManager(update_config)
        registry.register(driver.update)
