"""
Clean logger manager with RPC batching and local fallback.
"""

import asyncio
import logging
import logging.handlers
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
from collections import deque

from pydantic import BaseModel, Field

from unrealon_core.models.logging import LogEntryData, LogContext
from unrealon_core.models.websocket.logging import LogBatchMessage, LogBatchData
from unrealon_driver.utils.time import utc_now
from .base import BaseManager, ManagerConfig

logger = logging.getLogger(__name__)


class LoggerManagerConfig(ManagerConfig):
    """Logger manager configuration."""
    
    # Local logging
    log_file: Optional[str] = Field(default=None, description="Local log file path")
    max_file_size: int = Field(default=10485760, description="Max log file size (10MB)")
    backup_count: int = Field(default=5, description="Number of backup files")
    
    # RPC batching
    batch_size: int = Field(default=10, description="Logs per batch")
    batch_timeout: float = Field(default=5.0, description="Max batch wait time")
    
    # Driver info
    driver_id: str = Field(..., description="Driver ID for logs")


class LoggerManager(BaseManager):
    """
    Clean logger manager.
    
    Features:
    - Local file logging (always works)
    - RPC batching to server (when available)
    - Automatic fallback on RPC failure
    - Clean batch processing
    """
    
    def __init__(self, config: LoggerManagerConfig, websocket_client=None):
        super().__init__(config, "logger")
        self.config: LoggerManagerConfig = config
        self.websocket_client = websocket_client
        
        # Local logger setup
        self.local_logger = logging.getLogger(f"driver.{config.driver_id}")
        self._setup_local_logging()
        
        # RPC batching
        self._log_batch: deque = deque()
        self._batch_lock = asyncio.Lock()
        self._batch_task: Optional[asyncio.Task] = None
        self._running = False
    
    def _setup_local_logging(self):
        """Setup local file logging."""
        if not self.config.log_file:
            return
        
        try:
            # Create log directory if needed
            log_path = Path(self.config.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Setup rotating file handler
            handler = logging.handlers.RotatingFileHandler(
                self.config.log_file,
                maxBytes=self.config.max_file_size,
                backupCount=self.config.backup_count
            )
            
            # Set format
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            
            # Add to logger
            self.local_logger.addHandler(handler)
            self.local_logger.setLevel(getattr(logging, self.config.log_level))
            
        except Exception as e:
            logger.error(f"Failed to setup local logging: {e}")
    
    async def _initialize(self) -> bool:
        """Initialize logger manager."""
        try:
            # Start batch processor
            self._running = True
            self._batch_task = asyncio.create_task(self._batch_processor())
            
            logger.info("Logger manager initialized")
            return True
            
        except Exception as e:
            logger.error(f"Logger manager initialization failed: {e}")
            return False
    
    async def _shutdown(self):
        """Shutdown logger manager."""
        try:
            # Stop batch processor
            self._running = False
            
            if self._batch_task and not self._batch_task.done():
                self._batch_task.cancel()
                try:
                    await self._batch_task
                except asyncio.CancelledError:
                    pass
            
            # Send remaining logs
            if self._log_batch:
                await self._send_batch()
            
            logger.info("Logger manager shutdown complete")
            
        except Exception as e:
            logger.error(f"Logger manager shutdown error: {e}")
    
    async def _batch_processor(self):
        """Background task to process log batches."""
        while self._running:
            try:
                # Wait for batch timeout or until we have enough logs
                await asyncio.sleep(self.config.batch_timeout)
                
                async with self._batch_lock:
                    if len(self._log_batch) >= self.config.batch_size:
                        await self._send_batch()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Batch processor error: {e}")
                await asyncio.sleep(1.0)
    
    async def _send_batch(self):
        """Send current batch via RPC."""
        if not self._log_batch or not self.websocket_client:
            return
        
        try:
            # Get logs from batch
            logs_to_send = []
            while self._log_batch and len(logs_to_send) < self.config.batch_size:
                logs_to_send.append(self._log_batch.popleft())
            
            if not logs_to_send:
                return
            
            # Create batch message
            batch_data = LogBatchData(
                driver_id=self.config.driver_id,
                logs=logs_to_send,
                batch_timestamp=utc_now().isoformat()
            )
            batch_message = LogBatchMessage(data=batch_data)
            
            # Send via WebSocket
            self.websocket_client.send(batch_message)
            
            # Update stats
            self.stats.record_operation(True, 0.0)
            
        except Exception as e:
            logger.error(f"Failed to send log batch: {e}")
            # Put logs back in batch for retry
            for log_entry in reversed(logs_to_send):
                self._log_batch.appendleft(log_entry)
            
            self.stats.record_operation(False, 0.0)
    
    def log(self, level: str, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Log message with both local and RPC.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            context: Additional context data
        """
        try:
            # Always log locally first
            self._log_local(level, message, context)
            
            # Add to RPC batch if WebSocket available
            if self.websocket_client:
                self._add_to_batch(level, message, context)
                
        except Exception as e:
            logger.error(f"Logging failed: {e}")
    
    def _log_local(self, level: str, message: str, context: Optional[Dict[str, Any]] = None):
        """Log to local file."""
        try:
            # Format message with context
            if context:
                formatted_message = f"{message} | Context: {context}"
            else:
                formatted_message = message
            
            # Log at appropriate level
            log_level = getattr(logging, level.upper(), logging.INFO)
            self.local_logger.log(log_level, formatted_message)
            
        except Exception as e:
            logger.error(f"Local logging failed: {e}")
    
    def _add_to_batch(self, level: str, message: str, context: Optional[Dict[str, Any]] = None):
        """Add log to RPC batch."""
        try:
            # Create log entry
            log_context = LogContext()  # Use default empty context
            
            log_entry = LogEntryData(
                timestamp=utc_now().isoformat(),
                level=level.upper(),
                message=message,
                driver_id=self.config.driver_id,
                context=log_context
            )
            
            # Add to batch (thread-safe) - only if event loop is running
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self._add_to_batch_async(log_entry))
            except RuntimeError:
                # No running event loop - add directly to batch
                self._log_batch.append(log_entry)
            
        except Exception as e:
            logger.error(f"Failed to add log to batch: {e}")
    
    async def _add_to_batch_async(self, log_entry: LogEntryData):
        """Add log entry to batch asynchronously."""
        try:
            async with self._batch_lock:
                self._log_batch.append(log_entry)
                
                # Send immediately if batch is full
                if len(self._log_batch) >= self.config.batch_size:
                    await self._send_batch()
                    
        except Exception as e:
            logger.error(f"Failed to add log to batch async: {e}")
    
    # Convenience methods
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log debug message."""
        self.log("DEBUG", message, context)
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log info message."""
        self.log("INFO", message, context)
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log warning message."""
        self.log("WARNING", message, context)
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log error message."""
        self.log("ERROR", message, context)
    
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log critical message."""
        self.log("CRITICAL", message, context)
    
    async def _health_check(self) -> Dict[str, Any]:
        """Health check for logger."""
        return {
            "status": "ok",
            "batch_size": len(self._log_batch),
            "local_logging": self.config.log_file is not None,
            "rpc_logging": self.websocket_client is not None
        }
