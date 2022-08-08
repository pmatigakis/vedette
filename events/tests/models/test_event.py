from datetime import datetime, timedelta, timezone

from django.test import TestCase

from events.models import Event, RawEvent
from events.tests.factories import EventFactory


class EventTestsRuntimeTagValueTests(TestCase):
    def test_runtime_tag_value(self):
        event = Event(runtime_name="runtime", runtime_version="0.1")

        self.assertEqual(event.runtime_tag_value(), "runtime-0.1")

    def test_runtime_tag_value_without_name(self):
        event = Event(runtime_version="0.1")

        self.assertEqual(event.runtime_tag_value(), "0.1")

    def test_runtime_tag_value_without_version(self):
        event = Event(runtime_name="runtime")

        self.assertEqual(event.runtime_tag_value(), "runtime")


class EventUserDefinedTagsTests(TestCase):
    def test_user_defined_tags(self):
        raw_event = RawEvent(data={"tags": {"hello": "world"}})
        event = Event(raw_event=raw_event)

        self.assertDictEqual(event.user_defined_tags(), {"hello": "world"})

    def test_user_defined_tags_wthout_tags_in_the_raw_event(self):
        raw_event = RawEvent(data={})
        event = Event(raw_event=raw_event)

        self.assertDictEqual(event.user_defined_tags(), {})


class EventLogParamsTests(TestCase):
    def test_log_params(self):
        raw_event = RawEvent(data={"logentry": {"params": ["hello world"]}})
        event = Event(raw_event=raw_event)

        self.assertEqual(event.log_params(), ["hello world"])

    def test_log_params_without_params(self):
        raw_event = RawEvent(data={"logentry": {}})
        event = Event(raw_event=raw_event)

        self.assertEqual(event.log_params(), [])

    def test_log_params_without_log_entry(self):
        raw_event = RawEvent(data={})
        event = Event(raw_event=raw_event)

        self.assertEqual(event.log_params(), [])


class EventResolveTests(TestCase):
    def test_resolve(self):
        event = EventFactory()
        event.resolve()

        self.assertTrue(event.resolved)
        self.assertGreaterEqual(event.resolved_at, event.created_at)
        self.assertAlmostEqual(
            event.resolved_at,
            datetime.now(tz=timezone.utc),
            delta=timedelta(seconds=5),
        )

    def test_unserolve(self):
        event = EventFactory(resolved=True, resolved_at=datetime.now())
        event.unresolve()

        self.assertFalse(event.resolved)
        self.assertIsNone(event.resolved_at)
