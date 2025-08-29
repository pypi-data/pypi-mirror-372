"""
Alerts System

Simple alerting based on metrics and health checks.
Following critical requirements - max 500 lines, functions < 20 lines.

Phase 2: Core Systems - Monitoring
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Union
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict

from .health_check import HealthStatus
from .metrics import MetricsCollector, get_metrics_collector
from ..utils.time import utc_now


logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertRule(BaseModel):
    """Alert rule configuration."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    name: str = Field(description="Alert rule name")
    description: str = Field(description="Alert description")
    severity: AlertSeverity = Field(description="Alert severity")
    
    # Condition
    metric_name: Optional[str] = Field(default=None, description="Metric to monitor")
    threshold: Optional[float] = Field(default=None, description="Alert threshold")
    comparison: str = Field(default="gt", description="Comparison operator (gt, lt, eq, gte, lte)")
    
    # Health check condition
    component_name: Optional[str] = Field(default=None, description="Component to monitor")
    health_status: Optional[HealthStatus] = Field(default=None, description="Health status to alert on")
    
    # Timing
    duration_seconds: float = Field(default=60.0, description="How long condition must persist")
    cooldown_seconds: float = Field(default=300.0, description="Cooldown between alerts")
    
    # State
    enabled: bool = Field(default=True, description="Whether rule is enabled")
    last_triggered: Optional[datetime] = Field(default=None, description="Last trigger time")
    trigger_count: int = Field(default=0, description="Number of times triggered")


class Alert(BaseModel):
    """Active alert instance."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    alert_id: str = Field(description="Unique alert ID")
    rule_name: str = Field(description="Alert rule name")
    severity: AlertSeverity = Field(description="Alert severity")
    message: str = Field(description="Alert message")
    timestamp: datetime = Field(description="When alert was triggered")
    
    # Context
    metric_name: Optional[str] = Field(default=None, description="Related metric")
    metric_value: Optional[float] = Field(default=None, description="Metric value that triggered alert")
    component_name: Optional[str] = Field(default=None, description="Related component")
    
    # State
    acknowledged: bool = Field(default=False, description="Whether alert is acknowledged")
    resolved: bool = Field(default=False, description="Whether alert is resolved")
    resolved_at: Optional[datetime] = Field(default=None, description="When alert was resolved")


class AlertManager:
    """
    Simple alert manager.
    
    Monitors metrics and health checks, triggers alerts based on rules,
    and manages alert lifecycle.
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        """Initialize alert manager."""
        self.metrics_collector = metrics_collector or get_metrics_collector()
        self._rules: Dict[str, AlertRule] = {}
        self._active_alerts: Dict[str, Alert] = {}
        self._alert_handlers: List[Callable[[Alert], Any]] = []
        
        # State tracking
        self._rule_states: Dict[str, Dict[str, Any]] = {}
        self._running = False
        self._check_task: Optional[asyncio.Task] = None
        
        self.logger = logging.getLogger("alert_manager")
    
    def add_rule(self, rule: AlertRule) -> None:
        """Add alert rule."""
        self._rules[rule.name] = rule
        self._rule_states[rule.name] = {
            'condition_start': None,
            'last_check': None,
            'consecutive_triggers': 0
        }
        
        self.logger.info(f"Added alert rule: {rule.name} ({rule.severity})")
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove alert rule."""
        if rule_name in self._rules:
            del self._rules[rule_name]
            del self._rule_states[rule_name]
            self.logger.info(f"Removed alert rule: {rule_name}")
            return True
        return False
    
    def add_alert_handler(self, handler: Callable[[Alert], Any]) -> None:
        """Add alert handler function."""
        self._alert_handlers.append(handler)
        self.logger.debug(f"Added alert handler: {handler.__name__}")
    
    async def check_rules(self) -> List[Alert]:
        """Check all alert rules and trigger alerts if needed."""
        new_alerts = []
        
        for rule_name, rule in self._rules.items():
            if not rule.enabled:
                continue
            
            try:
                alert = await self._check_rule(rule)
                if alert:
                    new_alerts.append(alert)
            except Exception as e:
                self.logger.error(f"Error checking rule {rule_name}: {e}")
        
        return new_alerts
    
    async def _check_rule(self, rule: AlertRule) -> Optional[Alert]:
        """Check individual alert rule."""
        now = utc_now()
        rule_state = self._rule_states[rule.name]
        
        # Check cooldown
        if (rule.last_triggered and 
            (now - rule.last_triggered).total_seconds() < rule.cooldown_seconds):
            return None
        
        # Evaluate condition
        condition_met = await self._evaluate_condition(rule)
        
        if condition_met:
            # Track when condition started
            if rule_state['condition_start'] is None:
                rule_state['condition_start'] = now
            
            # Check if condition has persisted long enough
            condition_duration = (now - rule_state['condition_start']).total_seconds()
            
            if condition_duration >= rule.duration_seconds:
                # Trigger alert
                alert = await self._trigger_alert(rule)
                rule_state['condition_start'] = None  # Reset
                return alert
        else:
            # Condition not met, reset state
            rule_state['condition_start'] = None
        
        rule_state['last_check'] = now
        return None
    
    async def _evaluate_condition(self, rule: AlertRule) -> bool:
        """Evaluate alert rule condition."""
        # Metric-based condition
        if rule.metric_name and rule.threshold is not None:
            metric = await self.metrics_collector.get_metric(rule.metric_name)
            if not metric:
                return False
            
            value = metric.current_value
            threshold = rule.threshold
            
            if rule.comparison == "gt":
                return value > threshold
            elif rule.comparison == "lt":
                return value < threshold
            elif rule.comparison == "eq":
                return value == threshold
            elif rule.comparison == "gte":
                return value >= threshold
            elif rule.comparison == "lte":
                return value <= threshold
            else:
                return False
        
        # Health check condition
        if rule.component_name and rule.health_status:
            # This would integrate with health checker
            # For now, return False as placeholder
            return False
        
        return False
    
    async def _trigger_alert(self, rule: AlertRule) -> Alert:
        """Trigger alert for rule."""
        import uuid
        
        # Get current metric value for context
        metric_value = None
        if rule.metric_name:
            metric = await self.metrics_collector.get_metric(rule.metric_name)
            if metric:
                metric_value = metric.current_value
        
        # Create alert
        alert = Alert(
            alert_id=str(uuid.uuid4())[:8],
            rule_name=rule.name,
            severity=rule.severity,
            message=self._format_alert_message(rule, metric_value),
            timestamp=utc_now(),
            metric_name=rule.metric_name,
            metric_value=metric_value,
            component_name=rule.component_name
        )
        
        # Update rule state
        rule.last_triggered = utc_now()
        rule.trigger_count += 1
        
        # Store active alert
        self._active_alerts[alert.alert_id] = alert
        
        # Notify handlers
        await self._notify_handlers(alert)
        
        self.logger.warning(f"Alert triggered: {alert.rule_name} - {alert.message}")
        return alert
    
    def _format_alert_message(self, rule: AlertRule, metric_value: Optional[float]) -> str:
        """Format alert message."""
        if rule.metric_name and metric_value is not None:
            return (f"{rule.description} - {rule.metric_name} is {metric_value} "
                   f"({rule.comparison} {rule.threshold})")
        elif rule.component_name:
            return f"{rule.description} - {rule.component_name} is {rule.health_status}"
        else:
            return rule.description
    
    async def _notify_handlers(self, alert: Alert) -> None:
        """Notify all alert handlers."""
        for handler in self._alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception as e:
                self.logger.error(f"Error in alert handler {handler.__name__}: {e}")
    
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge alert."""
        if alert_id in self._active_alerts:
            self._active_alerts[alert_id].acknowledged = True
            self.logger.info(f"Alert acknowledged: {alert_id}")
            return True
        return False
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve alert."""
        if alert_id in self._active_alerts:
            alert = self._active_alerts[alert_id]
            alert.resolved = True
            alert.resolved_at = utc_now()
            self.logger.info(f"Alert resolved: {alert_id}")
            return True
        return False
    
    async def start_monitoring(self, check_interval: float = 30.0) -> None:
        """Start alert monitoring."""
        if self._running:
            self.logger.warning("Alert monitoring already running")
            return
        
        self._running = True
        self._check_task = asyncio.create_task(self._monitoring_loop(check_interval))
        
        self.logger.info(f"Started alert monitoring (interval: {check_interval}s)")
    
    async def stop_monitoring(self) -> None:
        """Stop alert monitoring."""
        self._running = False
        
        if self._check_task and not self._check_task.done():
            self._check_task.cancel()
            try:
                await self._check_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Stopped alert monitoring")
    
    async def _monitoring_loop(self, check_interval: float) -> None:
        """Background monitoring loop."""
        try:
            while self._running:
                await self.check_rules()
                await asyncio.sleep(check_interval)
                
        except asyncio.CancelledError:
            self.logger.debug("Alert monitoring loop cancelled")
            raise
        except Exception as e:
            self.logger.error(f"Error in alert monitoring loop: {e}")
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        return [alert for alert in self._active_alerts.values() if not alert.resolved]
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary."""
        active_alerts = self.get_active_alerts()
        
        severity_counts = {
            AlertSeverity.INFO: 0,
            AlertSeverity.WARNING: 0,
            AlertSeverity.ERROR: 0,
            AlertSeverity.CRITICAL: 0
        }
        
        for alert in active_alerts:
            severity_counts[alert.severity] += 1
        
        return {
            'total_rules': len(self._rules),
            'active_alerts': len(active_alerts),
            'severity_counts': severity_counts,
            'alerts': [alert.model_dump() for alert in active_alerts]
        }


# Global alert manager
_global_alert_manager = AlertManager()


def get_alert_manager() -> AlertManager:
    """Get global alert manager."""
    return _global_alert_manager


def alert_on_condition(
    name: str,
    metric_name: str,
    threshold: float,
    comparison: str = "gt",
    severity: AlertSeverity = AlertSeverity.WARNING,
    description: Optional[str] = None
) -> AlertRule:
    """
    Create and register alert rule for metric condition.
    
    Args:
        name: Alert rule name
        metric_name: Metric to monitor
        threshold: Alert threshold
        comparison: Comparison operator
        severity: Alert severity
        description: Alert description
        
    Returns:
        Created AlertRule
    """
    rule = AlertRule(
        name=name,
        description=description or f"{metric_name} {comparison} {threshold}",
        severity=severity,
        metric_name=metric_name,
        threshold=threshold,
        comparison=comparison
    )
    
    _global_alert_manager.add_rule(rule)
    return rule
