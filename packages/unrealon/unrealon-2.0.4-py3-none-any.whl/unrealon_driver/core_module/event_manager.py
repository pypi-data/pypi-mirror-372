"""
Clean event manager for module communication.
"""

import asyncio
import logging
from typing import Dict, List, Callable, Any, Optional
from collections import defaultdict

from .protocols import ModuleEvent, EventType

logger = logging.getLogger(__name__)


class EventManager:
    """
    Clean event manager for module communication.
    
    Provides pub/sub system for modules to communicate
    without tight coupling.
    """
    
    def __init__(self):
        self.listeners: Dict[EventType, List[Callable]] = defaultdict(list)
        self.event_queue: Optional[asyncio.Queue] = None
        self._processor_task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start(self):
        """Start event processing."""
        if self._running:
            return
        
        self._running = True
        # Only create task if there's a running event loop
        try:
            loop = asyncio.get_running_loop()
            self.event_queue = asyncio.Queue()
            self._processor_task = loop.create_task(self._process_events())
            logger.info("Event manager started")
        except RuntimeError:
            # No running event loop - don't start background processing
            logger.debug("No running event loop - EventManager running in sync mode")
    
    async def stop(self):
        """Stop event processing."""
        self._running = False
        
        if self._processor_task and not self._processor_task.done():
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
        
        # Clear queue
        self.event_queue = None
        self._processor_task = None
        
        logger.info("Event manager stopped")
    
    def subscribe(self, event_type: EventType, handler: Callable[[ModuleEvent], Any]):
        """Subscribe to event type."""
        self.listeners[event_type].append(handler)
        logger.debug(f"Subscribed handler to {event_type}")
    
    def unsubscribe(self, event_type: EventType, handler: Callable):
        """Unsubscribe from event type."""
        if handler in self.listeners[event_type]:
            self.listeners[event_type].remove(handler)
            logger.debug(f"Unsubscribed handler from {event_type}")
    
    async def emit(self, event: ModuleEvent):
        """Emit event to queue."""
        if self._running and self.event_queue:
            await self.event_queue.put(event)
    
    async def _process_events(self):
        """Background event processing."""
        while self._running:
            try:
                # Get event from queue
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                
                # Process event
                await self._handle_event(event)
                
            except asyncio.TimeoutError:
                # No events to process, continue
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Event processing error: {e}")
    
    async def _handle_event(self, event: ModuleEvent):
        """Handle single event."""
        try:
            handlers = self.listeners.get(event.event_type, [])
            
            if not handlers:
                logger.debug(f"No handlers for event type: {event.event_type}")
                return
            
            # Execute all handlers
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"Event handler error: {e}")
            
        except Exception as e:
            logger.error(f"Event handling error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event manager statistics."""
        return {
            "running": self._running,
            "listeners": {
                event_type.value: len(handlers)
                for event_type, handlers in self.listeners.items()
            },
            "queue_size": self.event_queue.qsize()
        }
