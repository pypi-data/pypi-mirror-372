"""
Monitoring Dashboard

Simple dashboard for system overview and monitoring data.
Following critical requirements - max 500 lines, functions < 20 lines.

Phase 2: Core Systems - Monitoring
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field, ConfigDict

from .health_check import HealthChecker, get_health_checker
from .metrics import MetricsCollector, get_metrics_collector
from .alerts import AlertManager, get_alert_manager
from ..utils.time import utc_now


logger = logging.getLogger(__name__)


class SystemStatus(BaseModel):
    """Overall system status."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    status: str = Field(description="Overall system status")
    uptime_seconds: float = Field(description="System uptime in seconds")
    timestamp: datetime = Field(default_factory=utc_now, description="Status timestamp")
    
    # Component counts
    total_components: int = Field(description="Total monitored components")
    healthy_components: int = Field(description="Healthy components")
    unhealthy_components: int = Field(description="Unhealthy components")
    
    # Alert counts
    total_alerts: int = Field(description="Total active alerts")
    critical_alerts: int = Field(description="Critical alerts")
    
    # Metrics
    total_metrics: int = Field(description="Total registered metrics")


class DashboardData(BaseModel):
    """Complete dashboard data."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    system_status: SystemStatus = Field(description="Overall system status")
    health_summary: Dict[str, Any] = Field(description="Health check summary")
    metrics_summary: Dict[str, Any] = Field(description="Metrics summary")
    alerts_summary: Dict[str, Any] = Field(description="Alerts summary")
    
    # Recent activity
    recent_alerts: List[Dict[str, Any]] = Field(description="Recent alerts")
    top_metrics: List[Dict[str, Any]] = Field(description="Top metrics by activity")
    
    # Performance indicators
    response_times: Dict[str, float] = Field(description="Average response times")
    error_rates: Dict[str, float] = Field(description="Error rates by component")


class MonitoringDashboard:
    """
    Monitoring dashboard aggregator.
    
    Collects data from health checks, metrics, and alerts
    to provide a unified system overview.
    """
    
    def __init__(
        self,
        health_checker: Optional[HealthChecker] = None,
        metrics_collector: Optional[MetricsCollector] = None,
        alert_manager: Optional[AlertManager] = None
    ):
        """Initialize monitoring dashboard."""
        self.health_checker = health_checker or get_health_checker()
        self.metrics_collector = metrics_collector or get_metrics_collector()
        self.alert_manager = alert_manager or get_alert_manager()
        
        self.start_time = utc_now()
        self.logger = logging.getLogger("monitoring_dashboard")
    
    async def get_system_status(self) -> SystemStatus:
        """Get overall system status."""
        # Get health summary
        health_data = self.health_checker.get_system_health()
        
        # Get alerts summary
        alerts_data = self.alert_manager.get_alert_summary()
        
        # Get metrics summary
        metrics_data = await self.metrics_collector.get_metrics_summary()
        
        # Calculate uptime
        uptime = (utc_now() - self.start_time).total_seconds()
        
        # Determine overall status
        if health_data['overall_status'] == 'unhealthy' or alerts_data['severity_counts']['critical'] > 0:
            overall_status = "critical"
        elif health_data['overall_status'] == 'degraded' or alerts_data['severity_counts']['error'] > 0:
            overall_status = "degraded"
        elif health_data['overall_status'] == 'healthy':
            overall_status = "healthy"
        else:
            overall_status = "unknown"
        
        return SystemStatus(
            status=overall_status,
            uptime_seconds=uptime,
            timestamp=utc_now(),
            total_components=health_data['summary']['total'],
            healthy_components=health_data['summary']['healthy'],
            unhealthy_components=health_data['summary']['unhealthy'],
            total_alerts=alerts_data['active_alerts'],
            critical_alerts=alerts_data['severity_counts']['critical'],
            total_metrics=metrics_data['total_metrics']
        )
    
    async def get_dashboard_data(self) -> DashboardData:
        """Get complete dashboard data."""
        # Collect all monitoring data
        system_status = await self.get_system_status()
        health_summary = self.health_checker.get_system_health()
        metrics_summary = await self.metrics_collector.get_metrics_summary()
        alerts_summary = self.alert_manager.get_alert_summary()
        
        # Get recent alerts (last 10)
        recent_alerts = alerts_summary['alerts'][-10:] if alerts_summary['alerts'] else []
        
        # Get top metrics by sample count
        top_metrics = []
        if metrics_summary['metrics']:
            sorted_metrics = sorted(
                metrics_summary['metrics'].items(),
                key=lambda x: x[1]['total_samples'],
                reverse=True
            )
            
            top_metrics = [
                {
                    'name': name,
                    'type': data['type'],
                    'current_value': data['current_value'],
                    'total_samples': data['total_samples']
                }
                for name, data in sorted_metrics[:10]
            ]
        
        # Calculate response times (placeholder)
        response_times = await self._calculate_response_times()
        
        # Calculate error rates (placeholder)
        error_rates = await self._calculate_error_rates()
        
        return DashboardData(
            system_status=system_status,
            health_summary=health_summary,
            metrics_summary=metrics_summary,
            alerts_summary=alerts_summary,
            recent_alerts=recent_alerts,
            top_metrics=top_metrics,
            response_times=response_times,
            error_rates=error_rates
        )
    
    async def _calculate_response_times(self) -> Dict[str, float]:
        """Calculate average response times by component."""
        response_times = {}
        
        # Look for timer metrics
        metrics = await self.metrics_collector.get_all_metrics()
        
        for name, metric in metrics.items():
            if metric.metric_type == "timer" and "response_time" in name:
                component = name.split("_")[0]  # Extract component name
                response_times[component] = metric.current_value
        
        return response_times
    
    async def _calculate_error_rates(self) -> Dict[str, float]:
        """Calculate error rates by component."""
        error_rates = {}
        
        # Look for error counter metrics
        metrics = await self.metrics_collector.get_all_metrics()
        
        for name, metric in metrics.items():
            if metric.metric_type == "counter" and "error" in name:
                component = name.split("_")[0]  # Extract component name
                
                # Calculate error rate (errors per minute)
                if metric.total_samples > 0:
                    time_diff = (utc_now() - metric.last_updated).total_seconds()
                    if time_diff > 0:
                        error_rates[component] = (metric.current_value / time_diff) * 60
        
        return error_rates
    
    async def get_component_details(self, component_name: str) -> Dict[str, Any]:
        """Get detailed information for specific component."""
        details = {
            'name': component_name,
            'timestamp': utc_now().isoformat()
        }
        
        # Health check details
        health_data = self.health_checker.get_system_health()
        if component_name in health_data['components']:
            details['health'] = health_data['components'][component_name]
        
        # Related metrics
        metrics = await self.metrics_collector.get_all_metrics()
        component_metrics = {}
        
        for name, metric in metrics.items():
            if component_name in name:
                component_metrics[name] = {
                    'type': metric.metric_type,
                    'current_value': metric.current_value,
                    'total_samples': metric.total_samples,
                    'last_updated': metric.last_updated.isoformat()
                }
        
        details['metrics'] = component_metrics
        
        # Related alerts
        active_alerts = self.alert_manager.get_active_alerts()
        component_alerts = [
            alert.model_dump() for alert in active_alerts
            if alert.component_name == component_name
        ]
        
        details['alerts'] = component_alerts
        
        return details
    
    async def export_dashboard_json(self) -> str:
        """Export dashboard data as JSON."""
        import json
        
        dashboard_data = await self.get_dashboard_data()
        
        # Convert to JSON-serializable format
        data_dict = dashboard_data.model_dump()
        
        # Custom JSON encoder for datetime objects
        def json_encoder(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        return json.dumps(data_dict, indent=2, default=json_encoder)
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics."""
        return {
            'uptime_seconds': (utc_now() - self.start_time).total_seconds(),
            'start_time': self.start_time.isoformat(),
            'components_monitored': len(self.health_checker._components),
            'metrics_registered': len(self.metrics_collector._metrics),
            'alert_rules': len(self.alert_manager._rules),
            'active_alerts': len(self.alert_manager.get_active_alerts())
        }


# Global dashboard instance
_global_dashboard = MonitoringDashboard()


def get_monitoring_dashboard() -> MonitoringDashboard:
    """Get global monitoring dashboard."""
    return _global_dashboard


async def get_system_overview() -> Dict[str, Any]:
    """Get quick system overview."""
    dashboard = get_monitoring_dashboard()
    
    system_status = await dashboard.get_system_status()
    
    return {
        'status': system_status.status,
        'uptime_seconds': system_status.uptime_seconds,
        'components': {
            'total': system_status.total_components,
            'healthy': system_status.healthy_components,
            'unhealthy': system_status.unhealthy_components
        },
        'alerts': {
            'total': system_status.total_alerts,
            'critical': system_status.critical_alerts
        },
        'metrics_count': system_status.total_metrics,
        'timestamp': system_status.timestamp.isoformat()
    }
