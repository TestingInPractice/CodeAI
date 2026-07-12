"""CodeAI Platform — Event Bus (extension point)."""

from collections import defaultdict
from datetime import datetime
from typing import Any, Callable

from scripts.core.types import Event


class EventBus:
    """Event Bus — extension point for subsystem communication.

    Status: Stub. Not required for initial implementation.
    Provided as extension point for future event-driven architecture.

    Events:
        spec.generated, spec.validated, spec.approved
        workflow.started, workflow.completed, workflow.rollback
        task.started, task.interrupted, task.completed
        knowledge.requested, knowledge.retrieved
        memory.stored, memory.loaded
        judge.evaluated, judge.routed

    API:
        subscribe(event, handler) -> None
        publish(event, data) -> None
    """

    def __init__(self):
        self._handlers: defaultdict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event: str, handler: Callable) -> None:
        """Subscribe to an event.

        Args:
            event: Event name (e.g., "spec.generated").
            handler: Callback function(event: Event).
        """
        self._handlers[event].append(handler)

    def publish(self, event: str, data: dict[str, Any]) -> None:
        """Publish an event.

        Args:
            event: Event name.
            data: Event data.
        """
        evt = Event(
            name=event,
            source=data.get("source", "unknown"),
            data=data,
            timestamp=datetime.now(),
        )
        for handler in self._handlers.get(event, []):
            handler(evt)
