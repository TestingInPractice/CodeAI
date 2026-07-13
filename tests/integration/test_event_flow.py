"""Integration Test: Event Flow.

Tests event flow through EventBus:
- wildcard subscriptions
- deduplication
- unsubscribe
- publish_raw
- publish
- correct event ordering
"""

import sys
import unittest
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.core.enums import EventType
from scripts.core.event_bus import EventBus
from scripts.core.types import Event


class TestEventFlow(unittest.TestCase):
    """Event Bus integration tests."""

    def test_exact_subscription(self):
        bus = EventBus()
        received = []
        bus.subscribe("task.started", lambda e: received.append(e.name))
        bus.publish("task.started", {"source": "test"})
        assert received == ["task.started"]

    def test_domain_wildcard(self):
        bus = EventBus()
        received = []
        bus.subscribe("task.*", lambda e: received.append(e.name))
        bus.publish("task.started", {"source": "test"})
        bus.publish("task.completed", {"source": "test"})
        bus.publish("judge.passed", {"source": "test"})
        assert received == ["task.started", "task.completed"]

    def test_catch_all_wildcard(self):
        bus = EventBus()
        received = []
        bus.subscribe("*", lambda e: received.append(e.name))
        bus.publish("task.started", {"source": "test"})
        bus.publish("judge.passed", {"source": "test"})
        bus.publish("knowledge.retrieved", {"source": "test"})
        assert len(received) == 3

    def test_deduplication(self):
        """Handler subscribed to both exact and wildcard fires once."""
        bus = EventBus()
        count = [0]
        def handler(e):
            count[0] += 1

        bus.subscribe("task.started", handler)
        bus.subscribe("task.*", handler)
        bus.subscribe("*", handler)

        bus.publish("task.started", {"source": "test"})
        assert count[0] == 1

    def test_unsubscribe(self):
        bus = EventBus()
        received = []
        handler = lambda e: received.append(e.name)
        bus.subscribe("task.started", handler)
        bus.publish("task.started", {"source": "test"})
        assert len(received) == 1

        bus.unsubscribe("task.started", handler)
        bus.publish("task.started", {"source": "test"})
        assert len(received) == 1  # Not called again

    def test_unsubscribe_not_found_raises(self):
        bus = EventBus()
        with self.assertRaises(ValueError):
            bus.unsubscribe("task.started", lambda e: None)

    def test_publish_raw(self):
        bus = EventBus()
        received = []
        bus.subscribe("task.started", lambda e: received.append(e))
        evt = Event(name="task.started", source="replay", data={"replay": True})
        bus.publish_raw(evt)
        assert len(received) == 1
        assert received[0].source == "replay"
        assert received[0].data["replay"] is True

    def test_publish_raw_with_wildcard(self):
        bus = EventBus()
        received = []
        bus.subscribe("task.*", lambda e: received.append(e.name))
        evt = Event(name="task.completed", source="test", data={})
        bus.publish_raw(evt)
        assert received == ["task.completed"]

    def test_event_envelope_fields(self):
        bus = EventBus()
        received = []
        bus.subscribe("task.started", lambda e: received.append(e))
        bus.publish("task.started", {"source": "ooda", "task_id": "abc"})
        evt = received[0]
        assert evt.name == "task.started"
        assert evt.source == "ooda"
        assert evt.data["task_id"] == "abc"
        assert evt.event_id is not None
        assert evt.timestamp is not None

    def test_source_default(self):
        bus = EventBus()
        received = []
        bus.subscribe("task.started", lambda e: received.append(e))
        bus.publish("task.started", {})
        assert received[0].source == "unknown"

    def test_event_type_enum(self):
        bus = EventBus()
        received = []
        bus.subscribe(EventType.TASK_STARTED, lambda e: received.append(e.name))
        bus.publish(EventType.TASK_STARTED, {"source": "test"})
        assert received == ["task.started"]

    def test_multiple_subscribers(self):
        bus = EventBus()
        results = {"a": [], "b": [], "c": []}
        bus.subscribe("task.started", lambda e: results["a"].append(1))
        bus.subscribe("task.started", lambda e: results["b"].append(1))
        bus.subscribe("task.*", lambda e: results["c"].append(1))
        bus.publish("task.started", {"source": "test"})
        assert len(results["a"]) == 1
        assert len(results["b"]) == 1
        assert len(results["c"]) == 1

    def test_ordering_preserved(self):
        """Events arrive in publish order."""
        bus = EventBus()
        order = []
        bus.subscribe("task.*", lambda e: order.append(e.data["seq"]))
        bus.publish("task.started", {"source": "test", "seq": 1})
        bus.publish("task.completed", {"source": "test", "seq": 2})
        bus.publish("task.started", {"source": "test", "seq": 3})
        assert order == [1, 2, 3]

    def test_no_subscribers_no_error(self):
        bus = EventBus()
        bus.publish("task.started", {"source": "test"})

    def test_publish_raw_no_subscribers(self):
        bus = EventBus()
        evt = Event(name="task.started", source="test", data={})
        bus.publish_raw(evt)

    def test_correlation_id(self):
        """Events can carry correlation_id."""
        bus = EventBus()
        received = []
        bus.subscribe("task.*", lambda e: received.append(e))
        corr = uuid4()
        bus.publish("task.started", {"source": "test"})
        # correlation_id is set on Event dataclass default (None)
        # We test it via publish_raw
        evt = Event(name="task.started", source="test", data={}, correlation_id=corr)
        bus.publish_raw(evt)
        assert received[1].correlation_id == corr
