from uuid import UUID

from django.test import TestCase

from projects.models import Project
from events.models import RawEvent, Event
from api.tasks import process_event


class ProcessEventTests(TestCase):
    def setUp(self):
        super(ProcessEventTests, self).setUp()

        self.project = Project(name="test project 1")
        self.project.save()

        self.event_data = {
            "event_id": "5d167e7d21004858ae9dfba46d370377",
            "timestamp": "2021-08-22T18:26:04.994971Z",
            "platform": "python"
        }

        self.raw_event = RawEvent(
            id=UUID(self.event_data["event_id"]),
            project=self.project,
            data=self.event_data
        )
        self.raw_event.save()

    def test_process_event_with_mandatory_event_data(self):
        process_event(self.event_data["event_id"])

        self.assertEqual(Event.objects.count(), 1)
        event = Event.objects.get(raw_event=self.raw_event)
        self.assertEqual(event.id, UUID(self.event_data["event_id"]))
        self.assertEqual(event.project, self.project)
        self.assertEqual(event.raw_event, self.raw_event)
