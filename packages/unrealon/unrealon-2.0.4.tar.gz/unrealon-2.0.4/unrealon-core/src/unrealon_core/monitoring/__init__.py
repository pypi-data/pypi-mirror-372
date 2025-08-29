"""
Monitoring Package

Basic monitoring and health checks for UnrealOn RPC system.
Following critical requirements - max 500 lines, 100% Pydantic v2.

Phase 2: Core Systems - Monitoring
"""

from .health_check import (
    HealthStatus, HealthCheckResult, ComponentHealth,
    HealthChecker, health_check_decorator
)
from .metrics import (
    MetricType, MetricValue, Metric,
    MetricsCollector, counter, gauge, histogram, timer
)
from .alerts import (
    AlertSeverity, AlertRule, Alert,
    AlertManager, alert_on_condition
)
from .dashboard import (
    DashboardData, SystemStatus,
    MonitoringDashboard, get_system_overview
)

__all__ = [
    # Health checks
    'HealthStatus', 'HealthCheckResult', 'ComponentHealth',
    'HealthChecker', 'health_check_decorator',
    
    # Metrics
    'MetricType', 'MetricValue', 'Metric',
    'MetricsCollector', 'counter', 'gauge', 'histogram', 'timer',
    
    # Alerts
    'AlertSeverity', 'AlertRule', 'Alert',
    'AlertManager', 'alert_on_condition',
    
    # Dashboard
    'DashboardData', 'SystemStatus',
    'MonitoringDashboard', 'get_system_overview',
]
