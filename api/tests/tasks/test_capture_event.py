from uuid import UUID

from django.test import TestCase

from api.tasks import capture_event
from events.models import Event, RawEvent
from projects.models import Project


class CaptureEventTests(TestCase):
    def setUp(self):
        super(CaptureEventTests, self).setUp()

        self.project = Project(name="test project 1")
        self.project.save()

    def test_capture_event(self):
        event_data = {
            "event_id": "5d167e7d21004858ae9dfba46d370377",
            "timestamp": "2021-08-22T18:26:04.994971Z",
            "platform": "python",
        }

        raw_event_id = capture_event(
            project_id=self.project.id,
            public_key=str(self.project.public_key),
            event_data=event_data,
        )

        self.assertIsNotNone(raw_event_id)
        self.assertEqual(RawEvent.objects.count(), 1)

        raw_event = RawEvent.objects.get(pk=raw_event_id)
        self.assertEqual(
            raw_event.id, UUID("5d167e7d21004858ae9dfba46d370377")
        )
        self.assertEqual(raw_event.project, self.project)
        self.assertDictEqual(raw_event.data, event_data)

        self.assertEqual(Event.objects.count(), 1)
        event = Event.objects.get(raw_event=raw_event)
        self.assertEqual(event.id, UUID(event_data["event_id"]))
        self.assertEqual(event.project, self.project)
        self.assertEqual(event.raw_event, raw_event)
