"""Tests for Event Bus."""

import unittest
from unittest.mock import MagicMock

from scripts.core.enums import EventType
from scripts.core.event_bus import EventBus
from scripts.core.types import Event


class TestSubscribe(unittest.TestCase):
    def setUp(self):
        self.bus = EventBus()

    def test_subscribe_exact(self):
        handler = MagicMock()
        self.bus.subscribe(EventType.TASK_STARTED, handler)
        self.assertEqual(len(self.bus._handlers["task.started"]), 1)

    def test_subscribe_string(self):
        handler = MagicMock()
        self.bus.subscribe("task.started", handler)
        self.assertEqual(len(self.bus._handlers["task.started"]), 1)

    def test_subscribe_wildcard_domain(self):
        handler = MagicMock()
        self.bus.subscribe("task.*", handler)
        self.assertEqual(len(self.bus._handlers["task.*"]), 1)

    def test_subscribe_wildcard_all(self):
        handler = MagicMock()
        self.bus.subscribe("*", handler)
        self.assertEqual(len(self.bus._handlers["*"]), 1)

    def test_multiple_handlers(self):
        h1 = MagicMock()
        h2 = MagicMock()
        self.bus.subscribe("task.started", h1)
        self.bus.subscribe("task.started", h2)
        self.assertEqual(len(self.bus._handlers["task.started"]), 2)


class TestUnsubscribe(unittest.TestCase):
    def setUp(self):
        self.bus = EventBus()

    def test_unsubscribe_removes_handler(self):
        handler = MagicMock()
        self.bus.subscribe("task.started", handler)
        self.bus.unsubscribe("task.started", handler)
        self.assertEqual(len(self.bus._handlers["task.started"]), 0)

    def test_unsubscribe_only_removes_target(self):
        h1 = MagicMock()
        h2 = MagicMock()
        self.bus.subscribe("task.started", h1)
        self.bus.subscribe("task.started", h2)
        self.bus.unsubscribe("task.started", h1)
        self.assertEqual(len(self.bus._handlers["task.started"]), 1)
        self.assertIn(h2, self.bus._handlers["task.started"])

    def test_unsubscribe_not_found_raises(self):
        handler = MagicMock()
        with self.assertRaises(ValueError):
            self.bus.unsubscribe("task.started", handler)

    def test_unsubscribe_event_type(self):
        handler = MagicMock()
        self.bus.subscribe(EventType.TASK_STARTED, handler)
        self.bus.unsubscribe(EventType.TASK_STARTED, handler)
        self.assertEqual(len(self.bus._handlers["task.started"]), 0)


class TestPublishExact(unittest.TestCase):
    def setUp(self):
        self.bus = EventBus()

    def test_publish_exact_match(self):
        handler = MagicMock()
        self.bus.subscribe("task.started", handler)
        self.bus.publish("task.started", {"source": "test"})
        handler.assert_called_once()
        evt = handler.call_args[0][0]
        self.assertEqual(evt.name, "task.started")
        self.assertEqual(evt.source, "test")

    def test_publish_no_match_not_called(self):
        handler = MagicMock()
        self.bus.subscribe("task.started", handler)
        self.bus.publish("task.completed", {"source": "test"})
        handler.assert_not_called()

    def test_publish_string(self):
        handler = MagicMock()
        self.bus.subscribe("task.started", handler)
        self.bus.publish("task.started", {"source": "test"})
        handler.assert_called_once()

    def test_publish_event_type(self):
        handler = MagicMock()
        self.bus.subscribe(EventType.TASK_STARTED, handler)
        self.bus.publish(EventType.TASK_STARTED, {"source": "test"})
        handler.assert_called_once()

    def test_publish_populates_event_fields(self):
        handler = MagicMock()
        self.bus.subscribe("task.started", handler)
        self.bus.publish("task.started", {"source": "ooda_runtime", "task_id": "abc"})
        evt = handler.call_args[0][0]
        self.assertIsInstance(evt.event_id, type(evt.event_id))
        self.assertIsNone(evt.correlation_id)
        self.assertEqual(evt.data["task_id"], "abc")
        self.assertIsNotNone(evt.timestamp)

    def test_publish_source_default(self):
        handler = MagicMock()
        self.bus.subscribe("task.started", handler)
        self.bus.publish("task.started", {})
        evt = handler.call_args[0][0]
        self.assertEqual(evt.source, "unknown")


class TestPublishWildcards(unittest.TestCase):
    def setUp(self):
        self.bus = EventBus()

    def test_domain_wildcard(self):
        handler = MagicMock()
        self.bus.subscribe("task.*", handler)
        self.bus.publish("task.started", {"source": "test"})
        self.bus.publish("task.completed", {"source": "test"})
        self.bus.publish("judge.passed", {"source": "test"})
        self.assertEqual(handler.call_count, 2)

    def test_catch_all_wildcard(self):
        handler = MagicMock()
        self.bus.subscribe("*", handler)
        self.bus.publish("task.started", {"source": "test"})
        self.bus.publish("judge.passed", {"source": "test"})
        self.bus.publish("knowledge.retrieved", {"source": "test"})
        self.assertEqual(handler.call_count, 3)

    def test_exact_and_wildcard_both_fire(self):
        exact = MagicMock()
        wildcard = MagicMock()
        self.bus.subscribe("task.started", exact)
        self.bus.subscribe("task.*", wildcard)
        self.bus.publish("task.started", {"source": "test"})
        exact.assert_called_once()
        wildcard.assert_called_once()

    def test_handler_not_called_twice(self):
        """If subscribed to both exact and wildcard, handler fires once."""
        handler = MagicMock()
        self.bus.subscribe("task.started", handler)
        self.bus.subscribe("task.*", handler)
        self.bus.publish("task.started", {"source": "test"})
        self.assertEqual(handler.call_count, 1)

    def test_wildcard_no_false_positives(self):
        handler = MagicMock()
        self.bus.subscribe("task.*", handler)
        self.bus.publish("judge.passed", {"source": "test"})
        handler.assert_not_called()

    def test_all_domains(self):
        handlers = {"task": MagicMock(), "judge": MagicMock(), "knowledge": MagicMock()}
        self.bus.subscribe("task.*", handlers["task"])
        self.bus.subscribe("judge.*", handlers["judge"])
        self.bus.subscribe("knowledge.*", handlers["knowledge"])
        self.bus.publish("task.started", {"source": "test"})
        self.bus.publish("judge.passed", {"source": "test"})
        self.bus.publish("knowledge.retrieved", {"source": "test"})
        for h in handlers.values():
            h.assert_called_once()


class TestPublishRaw(unittest.TestCase):
    def setUp(self):
        self.bus = EventBus()

    def test_publish_raw_dispatches(self):
        handler = MagicMock()
        self.bus.subscribe("task.started", handler)
        evt = Event(
            name="task.started",
            source="test",
            data={"key": "value"},
        )
        self.bus.publish_raw(evt)
        handler.assert_called_once_with(evt)

    def test_publish_raw_wildcard(self):
        handler = MagicMock()
        self.bus.subscribe("task.*", handler)
        evt = Event(name="task.completed", source="test", data={})
        self.bus.publish_raw(evt)
        handler.assert_called_once_with(evt)

    def test_publish_raw_no_envelope_creation(self):
        handler = MagicMock()
        self.bus.subscribe("task.started", handler)
        evt = Event(name="task.started", source="replay", data={"replay": True})
        self.bus.publish_raw(evt)
        received = handler.call_args[0][0]
        self.assertEqual(received.source, "replay")


class TestMultipleSubscribers(unittest.TestCase):
    def setUp(self):
        self.bus = EventBus()

    def test_multiple_subscribers_all_called(self):
        h1 = MagicMock()
        h2 = MagicMock()
        h3 = MagicMock()
        self.bus.subscribe("task.started", h1)
        self.bus.subscribe("task.*", h2)
        self.bus.subscribe("*", h3)
        self.bus.publish("task.started", {"source": "test"})
        h1.assert_called_once()
        h2.assert_called_once()
        h3.assert_called_once()

    def test_unsubscribe_doesnt_affect_others(self):
        h1 = MagicMock()
        h2 = MagicMock()
        self.bus.subscribe("task.started", h1)
        self.bus.subscribe("task.started", h2)
        self.bus.unsubscribe("task.started", h1)
        self.bus.publish("task.started", {"source": "test"})
        h1.assert_not_called()
        h2.assert_called_once()


class TestEdgeCases(unittest.TestCase):
    def setUp(self):
        self.bus = EventBus()

    def test_publish_no_subscribers(self):
        self.bus.publish("task.started", {"source": "test"})

    def test_publish_raw_no_subscribers(self):
        evt = Event(name="task.started", source="test", data={})
        self.bus.publish_raw(evt)

    def test_empty_data(self):
        handler = MagicMock()
        self.bus.subscribe("task.started", handler)
        self.bus.publish("task.started", {})
        handler.assert_called_once()

    def test_no_dot_in_name(self):
        handler = MagicMock()
        self.bus.subscribe("custom_event", handler)
        self.bus.publish("custom_event", {"source": "test"})
        handler.assert_called_once()


if __name__ == "__main__":
    unittest.main()
