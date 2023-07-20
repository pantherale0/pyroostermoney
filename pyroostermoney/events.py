"""Events publisher"""

from enum import Enum
from typing import Any

class EventType(Enum):
    """Valid event types"""
    UPDATED = 1
    CREATED = 2
    DELETED = 4
    ALL = 8

    def __str__(self) -> str:
        return self.name

class EventSource(Enum):
    """Valid event sources"""
    ALL = 0
    CHILD = 1
    FAMILY_ACCOUNT = 2
    JOBS = 4
    TRANSACTIONS = 8
    STANDING_ORDER = 16

    def __str__(self) -> str:
        return self.name

class Events():
    """Events for 3rd party services to attach to."""

    def __init__(self) -> None:
        self._subscriptions: dict[str, dict] = {}

    def subscribe(self, func: Any, source: EventSource, event_type: EventType, event_id: str):
        """Add an event subscription"""
        if event_id not in self._subscriptions:
            self._subscriptions[event_id] = {
                "func": func,
                "source": source,
                "type": event_type
            }
        else:
            raise KeyError("ID already subscribed")

    def unsubscribe(self, event_id: str):
        """Unsubscribe from an event"""
        if event_id in self._subscriptions:
            self._subscriptions.pop(event_id)
        else:
            raise KeyError("ID not subscribed")

    def fire_event(self, source: EventSource, event_type: EventType, metadata: dict = None):
        """Fires an event using the stored function"""
        subscribes = [x for x in self._subscriptions
                      if (self._subscriptions.get(x).get("source") == source or
                          self._subscriptions.get(x).get("source") == EventSource.ALL) and
                      (self._subscriptions.get(x).get("type") == event_type or
                       self._subscriptions.get(x).get("type") == EventType.ALL)]
        if len(subscribes) > 0:
            for subscribed in subscribes:
                subscribed = self._subscriptions.get(subscribed)
                metadata["source"] = str(source)
                metadata["type"] = str(event_type)
                func = subscribed.get("func")
                func(metadata)
