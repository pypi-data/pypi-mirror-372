"""
Metrics System

Lightweight metrics collection and aggregation.
Following critical requirements - max 500 lines, functions < 20 lines.

Phase 2: Core Systems - Monitoring
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from collections import defaultdict, deque

from pydantic import BaseModel, Field, ConfigDict

from ..utils.time import utc_now


logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Metric types."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class MetricValue(BaseModel):
    """Single metric value with timestamp."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    value: float = Field(description="Metric value")
    timestamp: datetime = Field(description="When value was recorded")
    labels: Dict[str, str] = Field(default_factory=dict, description="Metric labels")


class Metric(BaseModel):
    """Metric definition and current state."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    name: str = Field(description="Metric name")
    metric_type: MetricType = Field(description="Type of metric")
    description: str = Field(description="Metric description")
    current_value: float = Field(default=0.0, description="Current metric value")
    total_samples: int = Field(default=0, description="Total samples recorded")
    last_updated: datetime = Field(description="Last update timestamp")
    labels: Dict[str, str] = Field(default_factory=dict, description="Default labels")
    
    # Histogram-specific fields
    buckets: Optional[List[float]] = Field(default=None, description="Histogram buckets")
    bucket_counts: Optional[Dict[str, int]] = Field(default=None, description="Bucket counts")
    
    def update_value(self, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Update metric value."""
        self.current_value = value
        self.total_samples += 1
        self.last_updated = utc_now()
        
        if labels:
            self.labels.update(labels)
    
    def increment(self, amount: float = 1.0) -> None:
        """Increment counter metric."""
        if self.metric_type == MetricType.COUNTER:
            self.current_value += amount
            self.total_samples += 1
            self.last_updated = utc_now()
    
    def observe_histogram(self, value: float) -> None:
        """Observe value for histogram metric."""
        if self.metric_type != MetricType.HISTOGRAM or not self.buckets:
            return
        
        if not self.bucket_counts:
            self.bucket_counts = {str(bucket): 0 for bucket in self.buckets}
        
        # Find appropriate bucket
        for bucket in self.buckets:
            if value <= bucket:
                self.bucket_counts[str(bucket)] += 1
        
        self.total_samples += 1
        self.last_updated = utc_now()


class MetricsCollector:
    """
    Lightweight metrics collector.
    
    Collects and aggregates metrics for monitoring and alerting.
    Designed for simplicity and low overhead.
    """
    
    def __init__(self, max_history: int = 1000):
        """Initialize metrics collector."""
        self.max_history = max_history
        self._metrics: Dict[str, Metric] = {}
        self._history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self._lock = asyncio.Lock()
        self.logger = logging.getLogger("metrics_collector")
    
    async def register_metric(
        self,
        name: str,
        metric_type: MetricType,
        description: str,
        labels: Optional[Dict[str, str]] = None,
        buckets: Optional[List[float]] = None
    ) -> None:
        """
        Register new metric.
        
        Args:
            name: Metric name
            metric_type: Type of metric
            description: Metric description
            labels: Default labels
            buckets: Histogram buckets (for histogram metrics)
        """
        async with self._lock:
            if name in self._metrics:
                self.logger.warning(f"Metric {name} already registered")
                return
            
            metric = Metric(
                name=name,
                metric_type=metric_type,
                description=description,
                last_updated=utc_now(),
                labels=labels or {},
                buckets=buckets,
                bucket_counts={str(b): 0 for b in buckets} if buckets else None
            )
            
            self._metrics[name] = metric
            self.logger.debug(f"Registered metric: {name} ({metric_type})")
    
    async def record_counter(
        self, 
        name: str, 
        value: float = 1.0,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Record counter metric."""
        await self._record_metric(name, value, MetricType.COUNTER, labels)
    
    async def record_gauge(
        self, 
        name: str, 
        value: float,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Record gauge metric."""
        await self._record_metric(name, value, MetricType.GAUGE, labels)
    
    async def record_histogram(
        self, 
        name: str, 
        value: float,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Record histogram metric."""
        await self._record_metric(name, value, MetricType.HISTOGRAM, labels)
    
    async def record_timer(
        self, 
        name: str, 
        duration_seconds: float,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Record timer metric."""
        await self._record_metric(name, duration_seconds, MetricType.TIMER, labels)
    
    async def _record_metric(
        self,
        name: str,
        value: float,
        expected_type: MetricType,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Internal method to record metric value."""
        async with self._lock:
            if name not in self._metrics:
                # Auto-register metric
                await self.register_metric(name, expected_type, f"Auto-registered {expected_type} metric")
            
            metric = self._metrics[name]
            
            if metric.metric_type != expected_type:
                self.logger.error(f"Metric {name} type mismatch: expected {expected_type}, got {metric.metric_type}")
                return
            
            # Update metric based on type
            if metric.metric_type == MetricType.COUNTER:
                metric.increment(value)
            elif metric.metric_type == MetricType.HISTOGRAM:
                metric.observe_histogram(value)
            else:
                metric.update_value(value, labels)
            
            # Store in history
            metric_value = MetricValue(
                value=value,
                timestamp=utc_now(),
                labels=labels or {}
            )
            
            self._history[name].append(metric_value)
    
    async def get_metric(self, name: str) -> Optional[Metric]:
        """Get metric by name."""
        async with self._lock:
            return self._metrics.get(name)
    
    async def get_all_metrics(self) -> Dict[str, Metric]:
        """Get all registered metrics."""
        async with self._lock:
            return self._metrics.copy()
    
    async def get_metric_history(
        self, 
        name: str, 
        limit: Optional[int] = None
    ) -> List[MetricValue]:
        """Get metric history."""
        async with self._lock:
            history = list(self._history.get(name, []))
            
            if limit:
                history = history[-limit:]
            
            return history
    
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        async with self._lock:
            summary = {
                'total_metrics': len(self._metrics),
                'metrics_by_type': defaultdict(int),
                'metrics': {}
            }
            
            for name, metric in self._metrics.items():
                summary['metrics_by_type'][metric.metric_type] += 1
                
                summary['metrics'][name] = {
                    'type': metric.metric_type,
                    'current_value': metric.current_value,
                    'total_samples': metric.total_samples,
                    'last_updated': metric.last_updated.isoformat(),
                    'description': metric.description
                }
                
                # Add histogram-specific info
                if metric.metric_type == MetricType.HISTOGRAM and metric.bucket_counts:
                    summary['metrics'][name]['buckets'] = metric.bucket_counts
            
            return summary
    
    async def reset_metric(self, name: str) -> bool:
        """Reset metric to initial state."""
        async with self._lock:
            if name not in self._metrics:
                return False
            
            metric = self._metrics[name]
            metric.current_value = 0.0
            metric.total_samples = 0
            metric.last_updated = utc_now()
            
            if metric.bucket_counts:
                metric.bucket_counts = {bucket: 0 for bucket in metric.bucket_counts}
            
            # Clear history
            self._history[name].clear()
            
            self.logger.info(f"Reset metric: {name}")
            return True
    
    async def clear_all_metrics(self) -> None:
        """Clear all metrics and history."""
        async with self._lock:
            self._metrics.clear()
            self._history.clear()
            self.logger.info("Cleared all metrics")


# Global metrics collector
_global_metrics = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector."""
    return _global_metrics


def reset_global_metrics() -> None:
    """Reset global metrics collector (for testing)."""
    global _global_metrics
    _global_metrics = MetricsCollector()


# Convenience functions
async def counter(name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
    """Record counter metric."""
    await _global_metrics.record_counter(name, value, labels)


async def gauge(name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
    """Record gauge metric."""
    await _global_metrics.record_gauge(name, value, labels)


async def histogram(name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
    """Record histogram metric."""
    await _global_metrics.record_histogram(name, value, labels)


class MetricTimer:
    """Context manager for timing operations."""
    
    def __init__(self, metric_name: str, labels: Optional[Dict[str, str]] = None):
        self.metric_name = metric_name
        self.labels = labels
        self.start_time: Optional[datetime] = None
    
    async def __aenter__(self):
        self.start_time = utc_now()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (utc_now() - self.start_time).total_seconds()
            await _global_metrics.record_timer(self.metric_name, duration, self.labels)


def timer(metric_name: str, labels: Optional[Dict[str, str]] = None) -> MetricTimer:
    """Create metric timer context manager."""
    return MetricTimer(metric_name, labels)
