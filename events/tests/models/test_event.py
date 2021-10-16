from django.test import TestCase

from events.models import Event, RawEvent


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
