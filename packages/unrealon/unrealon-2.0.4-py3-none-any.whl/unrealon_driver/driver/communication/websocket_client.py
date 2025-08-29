"""
Clean WebSocket client with auto-reconnection and message queuing.
"""

import asyncio
import json
import logging
from typing import Optional, Callable, List
from collections import deque

import websockets
from websockets.asyncio.client import ClientConnection

from unrealon_core.models.websocket import (
    DriverRegistrationMessage,
    DriverRegistrationData,
    WebSocketMessage
)
from unrealon_core.enums.types import MessageType

logger = logging.getLogger(__name__)


class WebSocketClient:
    """
    Clean WebSocket client with robust connection management.
    
    Features:
    - Auto-reconnection with exponential backoff
    - Message queuing during disconnections
    - Background message processing
    - Clean error handling
    """
    
    def __init__(self, websocket_url: str, driver_id: str):
        self.websocket_url = websocket_url
        self.driver_id = driver_id
        self.websocket: Optional[ClientConnection] = None
        self.connected = False
        self.running = False
        
        # Message handling
        self.on_message: Optional[Callable[[WebSocketMessage], None]] = None
        self.message_queue: deque = deque()
        
        # Background tasks
        self._sender_task: Optional[asyncio.Task] = None
        self._receiver_task: Optional[asyncio.Task] = None
        self._monitor_task: Optional[asyncio.Task] = None
        
        # Reconnection settings
        self.reconnect_delay = 1.0
        self.max_reconnect_delay = 60.0
        self.reconnect_attempts = 0
    
    async def connect(self) -> bool:
        """Connect and start background tasks."""
        if self.running:
            return True
            
        self.running = True
        
        # Start background tasks
        self._sender_task = asyncio.create_task(self._message_sender())
        self._receiver_task = asyncio.create_task(self._message_receiver()) 
        self._monitor_task = asyncio.create_task(self._connection_monitor())
        
        return await self._establish_connection()
    
    async def disconnect(self):
        """Clean disconnect and stop all tasks."""
        self.running = False
        
        # Cancel background tasks
        for task in [self._sender_task, self._receiver_task, self._monitor_task]:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Close WebSocket
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        
        self.connected = False
        logger.info("WebSocket client stopped")
    
    async def _establish_connection(self) -> bool:
        """Establish WebSocket connection."""
        try:
            logger.info(f"Connecting to WebSocket: {self.websocket_url}")
            self.websocket = await websockets.connect(self.websocket_url)
            self.connected = True
            self.reconnect_attempts = 0
            self.reconnect_delay = 1.0
            logger.info("WebSocket connected successfully")
            return True
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            self.connected = False
            return False
    
    async def _connection_monitor(self):
        """Monitor connection and handle reconnection."""
        while self.running:
            if not self.connected and self.running:
                logger.info(f"Attempting reconnection (attempt {self.reconnect_attempts + 1})")
                
                if await self._establish_connection():
                    logger.info("Reconnection successful")
                else:
                    self.reconnect_attempts += 1
                    # Exponential backoff
                    self.reconnect_delay = min(
                        self.reconnect_delay * 2, 
                        self.max_reconnect_delay
                    )
                    await asyncio.sleep(self.reconnect_delay)
            else:
                await asyncio.sleep(5.0)  # Check every 5 seconds
    
    async def _message_sender(self):
        """Background task to send queued messages."""
        while self.running:
            if self.connected and self.websocket and self.message_queue:
                try:
                    message = self.message_queue.popleft()
                    await self.websocket.send(message)
                except (websockets.exceptions.ConnectionClosed, ConnectionResetError):
                    self.connected = False
                    # Put message back in queue
                    self.message_queue.appendleft(message)
                except Exception as e:
                    logger.error(f"Error sending message: {e}")
            else:
                await asyncio.sleep(0.1)
    
    async def _message_receiver(self):
        """Background task to receive messages."""
        while self.running:
            if self.connected and self.websocket:
                try:
                    message_str = await self.websocket.recv()
                    
                    # Parse and validate message
                    message_data = json.loads(message_str)
                    message = WebSocketMessage.model_validate(message_data)
                    
                    # Handle message
                    if self.on_message:
                        self.on_message(message)
                        
                except (websockets.exceptions.ConnectionClosed, ConnectionResetError):
                    self.connected = False
                    logger.warning("WebSocket connection lost")
                except Exception as e:
                    logger.error(f"Error receiving message: {e}")
            else:
                await asyncio.sleep(0.1)
    
    def send(self, message_data) -> None:
        """Queue message for sending."""
        if hasattr(message_data, 'model_dump_json'):
            # Pydantic model
            message_json = message_data.model_dump_json()
        else:
            # Raw data
            message_json = json.dumps(message_data)
        
        self.message_queue.append(message_json)
    
    async def register_driver(self, capabilities: List[str]) -> bool:
        """Register driver with capabilities."""
        try:
            # Create registration data
            registration_data = DriverRegistrationData(
                driver_id=self.driver_id,
                driver_name=self.driver_id,
                driver_type="universal",
                capabilities=capabilities
            )
            
            # Create registration message with correct type
            registration_message = DriverRegistrationMessage(data=registration_data)
            
            # Queue for sending
            self.send(registration_message)
            
            logger.info(f"Driver registration queued: {self.driver_id}")
            return True
            
        except Exception as e:
            logger.error(f"Driver registration failed: {e}")
            return False
