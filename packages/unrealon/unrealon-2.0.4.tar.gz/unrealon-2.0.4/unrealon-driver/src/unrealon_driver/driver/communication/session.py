"""
Clean driver session management.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from enum import Enum

from pydantic import BaseModel, Field

from unrealon_core.models.websocket import (
    TaskAssignmentData,
    TaskResultData,
    WebSocketMessage
)
from unrealon_core.enums import DriverStatus, TaskStatus, MessageType
from unrealon_driver.utils.time import utc_now

logger = logging.getLogger(__name__)


class SessionStatus(str, Enum):
    """Clean session status."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting" 
    CONNECTED = "connected"
    REGISTERED = "registered"
    ACTIVE = "active"
    ERROR = "error"


class SessionStats(BaseModel):
    """Session statistics."""
    connected_at: Optional[datetime] = None
    registered_at: Optional[datetime] = None
    tasks_completed: int = 0
    tasks_failed: int = 0
    last_activity: Optional[datetime] = None


class DriverSession:
    """
    Clean session manager.
    
    Handles connection, registration, and task processing
    with simple, clear interface.
    """
    
    def __init__(self, driver_id: str, websocket_client=None):
        self.driver_id = driver_id
        self.websocket_client = websocket_client
        self.status = SessionStatus.DISCONNECTED
        self.stats = SessionStats()
        
        # Task handling
        self.task_handlers: Dict[str, Callable] = {}
        
        # Setup WebSocket message handler
        if self.websocket_client:
            self.websocket_client.on_message = self._handle_websocket_message
    
    async def start_session(self, capabilities: List[str] = None) -> bool:
        """Start session with registration."""
        if not self.websocket_client:
            logger.error("No WebSocket client configured")
            return False
        
        try:
            # Connect WebSocket
            self.status = SessionStatus.CONNECTING
            if not await self.websocket_client.connect():
                self.status = SessionStatus.ERROR
                return False
            
            self.status = SessionStatus.CONNECTED
            self.stats.connected_at = utc_now()
            
            # Register driver
            if await self.register(capabilities or []):
                self.status = SessionStatus.REGISTERED
                self.stats.registered_at = utc_now()
                logger.info(f"Session started for driver: {self.driver_id}")
                return True
            else:
                self.status = SessionStatus.ERROR
                return False
                
        except Exception as e:
            logger.error(f"Session start failed: {e}")
            self.status = SessionStatus.ERROR
            return False
    
    async def stop_session(self):
        """Stop session cleanly."""
        try:
            if self.websocket_client:
                await self.websocket_client.disconnect()
            
            self.status = SessionStatus.DISCONNECTED
            logger.info(f"Session stopped for driver: {self.driver_id}")
            
        except Exception as e:
            logger.error(f"Session stop error: {e}")
    
    async def register(self, capabilities: List[str]) -> bool:
        """Register driver with capabilities."""
        if not self.websocket_client:
            return False
        
        try:
            success = await self.websocket_client.register_driver(capabilities)
            if success:
                logger.info(f"Driver registered: {self.driver_id} with capabilities: {capabilities}")
            return success
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return False
    
    def register_task_handler(self, task_type: str, handler: Callable):
        """Register handler for task type."""
        self.task_handlers[task_type] = handler
        logger.debug(f"Registered handler for task type: {task_type}")
    
    def _handle_websocket_message(self, message: WebSocketMessage):
        """Handle incoming WebSocket messages."""
        try:
            self.stats.last_activity = utc_now()
            
            if message.type == MessageType.TASK_ASSIGN:
                asyncio.create_task(self._handle_task_assignment(message))
            else:
                logger.debug(f"Received message type: {message.type}")
                
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
    
    async def _handle_task_assignment(self, message: WebSocketMessage):
        """Handle task assignment."""
        try:
            # Validate task data
            task_data = TaskAssignmentData.model_validate(message.data)
            
            # Find handler
            handler = self.task_handlers.get(task_data.task_type)
            if not handler:
                logger.warning(f"No handler for task type: {task_data.task_type}")
                await self._send_task_result(
                    task_data.task_id,
                    TaskStatus.FAILED,
                    error="No handler for task type"
                )
                return
            
            # Execute task
            try:
                result = await handler(task_data)
                await self._send_task_result(
                    task_data.task_id,
                    TaskStatus.COMPLETED,
                    result=result
                )
                self.stats.tasks_completed += 1
                
            except Exception as e:
                logger.error(f"Task execution failed: {e}")
                await self._send_task_result(
                    task_data.task_id,
                    TaskStatus.FAILED,
                    error=str(e)
                )
                self.stats.tasks_failed += 1
                
        except Exception as e:
            logger.error(f"Task assignment handling failed: {e}")
    
    async def _send_task_result(self, task_id: str, status: TaskStatus, result: Any = None, error: str = None):
        """Send task result back."""
        try:
            result_data = TaskResultData(
                task_id=task_id,
                driver_id=self.driver_id,
                status=status,
                result=result,
                error_message=error,
                completed_at=utc_now()
            )
            
            if self.websocket_client:
                self.websocket_client.send(result_data)
                
        except Exception as e:
            logger.error(f"Failed to send task result: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get session status."""
        return {
            "driver_id": self.driver_id,
            "status": self.status.value,
            "stats": self.stats.model_dump(),
            "handlers": list(self.task_handlers.keys())
        }
