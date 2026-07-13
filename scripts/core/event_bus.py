"""CodeAI Platform — Event Bus.

Provides publish/subscribe communication between subsystems.
Supports exact match, domain wildcards ("task.*"), and catch-all ("*").
"""

from collections import defaultdict
from datetime import datetime
from typing import Any, Callable, Union

from scripts.core.enums import EventType
from scripts.core.types import Event


class EventBus:
    """Event Bus for inter-subsystem communication.

    API:
        subscribe(event, handler) -> None
        unsubscribe(event, handler) -> None
        publish(event, data) -> None
        publish_raw(event) -> None

    Wildcard support:
        "task.*"   — matches all task events
        "judge.*"  — matches all judge events
        "*"        — matches all events
    """

    def __init__(self):
        self._handlers: defaultdict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event: Union[EventType, str], handler: Callable) -> None:
        """Subscribe to an event by name or EventType.

        Args:
            event: EventType enum or event name string. Supports wildcards.
            handler: Callback function(event: Event).
        """
        pattern = event.value if isinstance(event, EventType) else event
        self._handlers[pattern].append(handler)

    def unsubscribe(self, event: Union[EventType, str], handler: Callable) -> None:
        """Remove a subscription.

        Args:
            event: EventType enum or event name string.
            handler: The handler to remove.

        Raises:
            ValueError: If handler not found for this event.
        """
        pattern = event.value if isinstance(event, EventType) else event
        handlers = self._handlers.get(pattern, [])
        if handler not in handlers:
            raise ValueError(f"Handler not found for event '{pattern}'")
        handlers.remove(handler)

    def publish(self, event: Union[EventType, str], data: dict[str, Any]) -> None:
        """Publish an event. Creates Event envelope automatically.

        Args:
            event: EventType enum or event name string.
            data: Event payload dict.
        """
        name = event.value if isinstance(event, EventType) else event
        evt = Event(
            name=name,
            source=data.pop("source", "unknown"),
            data=data,
            timestamp=datetime.now(),
        )
        self._dispatch(evt)

    def publish_raw(self, event: Event) -> None:
        """Publish a pre-built Event (for replay/logging).

        Args:
            event: Pre-built Event envelope.
        """
        self._dispatch(event)

    def _dispatch(self, event: Event) -> None:
        """Dispatch event to matching handlers."""
        handled: set[int] = set()
        name = event.name
        domain = name.split(".")[0] if "." in name else ""

        for pattern, handlers in self._handlers.items():
            if self._matches(pattern, name, domain):
                for handler in handlers:
                    h_id = id(handler)
                    if h_id not in handled:
                        handled.add(h_id)
                        handler(event)

    @staticmethod
    def _matches(pattern: str, name: str, domain: str) -> bool:
        """Check if a subscription pattern matches an event name."""
        if pattern == "*":
            return True
        if pattern == name:
            return True
        if pattern.endswith(".*") and pattern[:-2] == domain:
            return True
        return False
