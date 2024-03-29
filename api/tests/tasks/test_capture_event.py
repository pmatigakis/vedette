from datetime import datetime, timezone
from uuid import UUID

from django.test import TestCase

from api.exceptions import InvalidEventData
from api.tasks import capture_event
from events.models import Event, Issue, Project, RawEvent


class CaptureEventTests(TestCase):
    def setUp(self):
        super(CaptureEventTests, self).setUp()

        self.project = Project(name="test project 1")
        self.project.save()

    def test_capture_event(self):
        event_message = "msg"
        event_data = {
            "event_id": "5d167e7d21004858ae9dfba46d370377",
            "timestamp": "2021-08-22T18:26:04.994971Z",
            "platform": "python",
            "message": event_message,
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

        event_timestamp = datetime(
            2021, 8, 22, 18, 26, 4, 994971, tzinfo=timezone.utc
        )

        self.assertEqual(Event.objects.count(), 1)
        event = Event.objects.get(raw_event=raw_event)
        self.assertEqual(event.id, UUID(event_data["event_id"]))
        self.assertEqual(event.project, self.project)
        self.assertEqual(event.raw_event, raw_event)
        self.assertEqual(event.timestamp, event_timestamp)
        self.assertEqual(event.platform, "python")
        self.assertEqual(event.message, event_message)

        issues = Issue.objects.all()
        self.assertEqual(len(issues), 1)
        issue = issues[0]
        self.assertEqual(issue.primary_event, event)
        self.assertEqual(issue.project, self.project)
        self.assertEqual(
            issue.signature,
            "58939aecce76e0dc21230f1a60bad39fbf84837cf1ea2954ef0f03167b16f660",
        )
        self.assertEqual(
            issue.first_seen_at,
            event_timestamp,
        )
        self.assertEqual(issue.last_seen_at, issue.first_seen_at)
        self.assertEqual(event.issue, issue)

    def test_capture_event_without_message(self):
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

        event_timestamp = datetime(
            2021, 8, 22, 18, 26, 4, 994971, tzinfo=timezone.utc
        )

        self.assertEqual(Event.objects.count(), 1)
        event = Event.objects.get(raw_event=raw_event)
        self.assertEqual(event.id, UUID(event_data["event_id"]))
        self.assertEqual(event.project, self.project)
        self.assertEqual(event.raw_event, raw_event)
        self.assertIsNone(event.issue)
        self.assertEqual(event.timestamp, event_timestamp)
        self.assertEqual(event.platform, "python")

        issues = Issue.objects.all()
        self.assertEqual(len(issues), 0)

    def test_capture_event_with_missing_required_field(self):
        event_data = {
            "event_id": "5d167e7d21004858ae9dfba46d370377",
            "timestamp": "2021-08-22T18:26:04.994971Z",
            "platform": "python",
        }

        for required_field_name in event_data.keys():
            modified_event_data = event_data.copy()
            del modified_event_data[required_field_name]

            self.assertRaises(
                InvalidEventData,
                capture_event,
                project_id=self.project.id,
                public_key=str(self.project.public_key),
                event_data=modified_event_data,
            )

            self.assertEqual(RawEvent.objects.count(), 0)
            self.assertEqual(Event.objects.count(), 0)
            self.assertEqual(Issue.objects.count(), 0)
