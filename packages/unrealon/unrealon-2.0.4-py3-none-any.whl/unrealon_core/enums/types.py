"""
Type enums for UnrealOn system.

These enums define types for messages, proxies, tasks, and other
system components. They ensure type safety and consistent
categorization throughout the system.

Phase 1: Foundation type enums
"""

from enum import Enum


class MessageType(str, Enum):
    """
    WebSocket message types for driver communication.
    
    Defines all possible message types that can be sent
    between the system and drivers via WebSocket.
    """
    
    # Driver lifecycle messages
    DRIVER_REGISTER = "driver_register"           # Driver registration request
    DRIVER_REGISTER_RESPONSE = "driver_register_response"  # Registration response
    DRIVER_HEARTBEAT = "driver_heartbeat"         # Driver heartbeat/ping
    DRIVER_STATUS = "driver_status"               # Driver status update
    DRIVER_DISCONNECT = "driver_disconnect"      # Driver disconnect notification
    
    # Task management messages
    TASK_ASSIGN = "task_assign"                   # Assign task to driver
    TASK_RESULT = "task_result"                   # Task result from driver
    TASK_ERROR = "task_error"                     # Task error from driver
    TASK_PROGRESS = "task_progress"               # Task progress update
    TASK_CANCEL = "task_cancel"                   # Cancel task request
    
    # Command messages
    COMMAND_START = "command_start"               # Start command
    COMMAND_STOP = "command_stop"                 # Stop command
    COMMAND_RESTART = "command_restart"           # Restart command
    COMMAND_PAUSE = "command_pause"               # Pause command
    COMMAND_RESUME = "command_resume"             # Resume command
    COMMAND_CONFIG_UPDATE = "command_config_update"  # Update configuration
    
    # Proxy management messages
    PROXY_REQUEST = "proxy_request"               # Request proxy from pool
    PROXY_RESPONSE = "proxy_response"             # Proxy response
    PROXY_HEALTH_REPORT = "proxy_health_report"  # Report proxy health
    PROXY_ROTATION_REQUEST = "proxy_rotation_request"  # Request proxy rotation
    PROXY_RELEASE = "proxy_release"              # Release proxy assignment
    
    # Logging messages
    LOG_MESSAGE = "log_message"                   # Log message from driver
    LOG_BATCH = "log_batch"                       # Batch of log messages
    
    # System messages
    PING = "ping"                                 # Ping message
    PONG = "pong"                                 # Pong response
    ERROR = "error"                               # Error message
    ACK = "ack"                                   # Acknowledgment
    
    def is_driver_lifecycle(self) -> bool:
        """Check if message is related to driver lifecycle."""
        return self in [
            MessageType.DRIVER_REGISTER,
            MessageType.DRIVER_REGISTER_RESPONSE,
            MessageType.DRIVER_HEARTBEAT,
            MessageType.DRIVER_STATUS,
            MessageType.DRIVER_DISCONNECT
        ]
    
    def is_task_related(self) -> bool:
        """Check if message is related to task management."""
        return self in [
            MessageType.TASK_ASSIGN,
            MessageType.TASK_RESULT,
            MessageType.TASK_ERROR,
            MessageType.TASK_PROGRESS,
            MessageType.TASK_CANCEL
        ]
    
    def is_command(self) -> bool:
        """Check if message is a command."""
        return self.value.startswith("command_")
    
    def requires_response(self) -> bool:
        """Check if message type requires a response."""
        return self in [
            MessageType.DRIVER_REGISTER,
            MessageType.PROXY_REQUEST,
            MessageType.PING
        ]


class ProxyType(str, Enum):
    """
    Proxy server types supported by the system.
    
    Defines the different types of proxy servers
    that can be used for web requests.
    """
    
    HTTP = "http"                  # HTTP proxy
    HTTPS = "https"                # HTTPS proxy
    SOCKS4 = "socks4"             # SOCKS4 proxy
    SOCKS5 = "socks5"             # SOCKS5 proxy
    
    def supports_https(self) -> bool:
        """Check if proxy type supports HTTPS."""
        return self in [ProxyType.HTTPS, ProxyType.SOCKS5]
    
    def is_socks(self) -> bool:
        """Check if proxy is a SOCKS proxy."""
        return self in [ProxyType.SOCKS4, ProxyType.SOCKS5]
    
    def get_default_port(self) -> int:
        """Get default port for proxy type."""
        ports = {
            ProxyType.HTTP: 8080,
            ProxyType.HTTPS: 8080,
            ProxyType.SOCKS4: 1080,
            ProxyType.SOCKS5: 1080,
        }
        return ports.get(self, 8080)


class TaskPriority(str, Enum):
    """
    Task priority levels for queue management.
    
    Defines priority levels that determine the order
    in which tasks are processed by drivers.
    """
    
    LOW = "low"                    # Low priority task
    NORMAL = "normal"              # Normal priority task (default)
    HIGH = "high"                  # High priority task
    URGENT = "urgent"              # Urgent priority task
    CRITICAL = "critical"          # Critical priority task
    
    def get_numeric_priority(self) -> int:
        """Get numeric priority for sorting (higher = more urgent)."""
        priorities = {
            TaskPriority.LOW: 1,
            TaskPriority.NORMAL: 5,
            TaskPriority.HIGH: 10,
            TaskPriority.URGENT: 20,
            TaskPriority.CRITICAL: 50,
        }
        return priorities.get(self, 5)
    
    def is_urgent(self) -> bool:
        """Check if task has urgent or critical priority."""
        return self in [TaskPriority.URGENT, TaskPriority.CRITICAL]
    
    @classmethod
    def from_numeric(cls, priority: int) -> 'TaskPriority':
        """Create TaskPriority from numeric value."""
        if priority >= 50:
            return cls.CRITICAL
        elif priority >= 20:
            return cls.URGENT
        elif priority >= 10:
            return cls.HIGH
        elif priority >= 5:
            return cls.NORMAL
        else:
            return cls.LOW


class DriverType(str, Enum):
    """
    Driver types for categorization and capability matching.
    
    Defines different types of drivers based on their
    primary functionality and target websites.
    """
    
    # General purpose
    UNIVERSAL = "universal"        # Universal driver for any site
    GENERIC = "generic"           # Generic web scraping driver
    
    # E-commerce specific
    ECOMMERCE = "ecommerce"       # E-commerce sites
    MARKETPLACE = "marketplace"    # Online marketplaces
    PRODUCT_CATALOG = "product_catalog"  # Product catalogs
    
    # Content specific
    NEWS = "news"                 # News websites
    BLOG = "blog"                 # Blog sites
    SOCIAL_MEDIA = "social_media" # Social media platforms
    
    # Data specific
    API = "api"                   # API-based data collection
    DATABASE = "database"         # Database extraction
    FILE = "file"                 # File processing
    
    def is_web_scraping(self) -> bool:
        """Check if driver type involves web scraping."""
        return self in [
            DriverType.UNIVERSAL,
            DriverType.GENERIC,
            DriverType.ECOMMERCE,
            DriverType.MARKETPLACE,
            DriverType.PRODUCT_CATALOG,
            DriverType.NEWS,
            DriverType.BLOG,
            DriverType.SOCIAL_MEDIA
        ]
    
    def requires_browser(self) -> bool:
        """Check if driver type typically requires a browser."""
        return self in [
            DriverType.ECOMMERCE,
            DriverType.MARKETPLACE,
            DriverType.SOCIAL_MEDIA
        ]


class ConfigType(str, Enum):
    """
    Configuration types for different system components.
    
    Used to categorize and validate different types
    of configuration objects in the system.
    """
    
    SYSTEM = "system"             # System-wide configuration
    DRIVER = "driver"             # Driver-specific configuration
    HTTP = "http"                 # HTTP client configuration
    PROXY = "proxy"               # Proxy management configuration
    BROWSER = "browser"           # Browser automation configuration
    LOGGING = "logging"           # Logging configuration
    CACHE = "cache"               # Cache configuration
    THREAD = "thread"             # Threading configuration
    DATABASE = "database"         # Database configuration
    SECURITY = "security"         # Security configuration
    
    def get_config_schema(self) -> str:
        """Get the schema identifier for this config type."""
        return f"unrealon.config.{self.value}"
