from uuid import UUID
from django.test import TestCase

from projects.models import Project
from events.models import RawEvent, Event

from api.tasks import capture_event


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
        self.assertEqual(Event.objects.count(), 0)
        self.assertEqual(RawEvent.objects.count(), 1)

        raw_event = RawEvent.objects.get(pk=raw_event_id)
        self.assertEqual(
            raw_event.id, UUID("5d167e7d21004858ae9dfba46d370377")
        )
        self.assertEqual(raw_event.project, self.project)
        self.assertDictEqual(raw_event.data, event_data)
