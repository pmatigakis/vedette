from django.test import TestCase

from events.models import RawEvent


class RawEventTests(TestCase):
    def test_pretty_json_data(self):
        raw_event = RawEvent(data={"hello": "world"})

        self.assertEqual(
            raw_event.pretty_json_data(),
            """{
    "hello": "world"
}"""
        )
