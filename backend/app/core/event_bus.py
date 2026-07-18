import asyncio
import logging
from typing import Dict, List, Callable, Any, Awaitable

logger = logging.getLogger("app.core.event_bus")

class EventBus:
    _listeners: Dict[str, List[Callable[[Any], Awaitable[None]]]] = {}

    @classmethod
    def subscribe(cls, event_type: str, handler: Callable[[Any], Awaitable[None]]):
        """
        Subscribes an async handler function to an event type.
        """
        if event_type not in cls._listeners:
            cls._listeners[event_type] = []
        cls._listeners[event_type].append(handler)
        logger.debug(f"Subscribed handler to event '{event_type}'")

    @classmethod
    async def publish(cls, event_type: str, data: Any):
        """
        Publishes event data to all registered async handlers.
        """
        if event_type not in cls._listeners:
            return
            
        logger.info(f"Publishing event '{event_type}' with data: {data}")
        tasks = []
        for handler in cls._listeners[event_type]:
            tasks.append(asyncio.create_task(handler(data)))
            
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
