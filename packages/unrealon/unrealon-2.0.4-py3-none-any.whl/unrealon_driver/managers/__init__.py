"""
Clean manager system for UnrealOn Driver.
"""

from .base import BaseManager, ManagerConfig, ManagerStatus
from .logger import LoggerManager, LoggerManagerConfig
from .http import HttpManager, HttpManagerConfig
from .browser import BrowserManager, BrowserManagerConfig
from .cache import CacheManager, CacheManagerConfig
from .proxy import ProxyManager, ProxyManagerConfig
from .threading import ThreadManager, ThreadManagerConfig
from .update import UpdateManager, UpdateManagerConfig
from .registry import ManagerRegistry

__all__ = [
    # Base
    "BaseManager",
    "ManagerConfig", 
    "ManagerStatus",
    
    # Managers
    "LoggerManager", "LoggerManagerConfig",
    "HttpManager", "HttpManagerConfig",
    "BrowserManager", "BrowserManagerConfig",
    "CacheManager", "CacheManagerConfig",
    "ProxyManager", "ProxyManagerConfig",
    "ThreadManager", "ThreadManagerConfig",
    "UpdateManager", "UpdateManagerConfig",
    
    # Registry
    "ManagerRegistry",
]
