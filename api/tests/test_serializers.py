from datetime import timezone, timedelta, datetime
from uuid import UUID

from django.test import TestCase

from api.serializers import RawEventSerializer, EventSerializer
from events.models import RawEvent, Event
from projects.models import Project


class RawEventSerializerTests(TestCase):
    def setUp(self):
        super(RawEventSerializerTests, self).setUp()

        self.project = Project(name="test project 1")
        self.project.save()

    def test_validate_valid_data(self):
        data = {
            "event_id": "b553a92eaba94939b4e4d6725253c1c5",
            "timestamp": "2021-08-22T18:19:51.690616Z",
            "platform": "python"
        }
        serializer = RawEventSerializer(data=data)

        self.assertTrue(serializer.is_valid())

    def test_validate_invalid_data(self):
        data = {
            "event_id": "b553a92eaba94939b4e4d6725253c1c5",
            "timestamp": "2021-08-22T18:19:51.690616Z",
            "platform": "python"
        }

        for key in data.keys():
            data_copy = data.copy()
            del data_copy[key]
            serializer = RawEventSerializer(data=data_copy)

            self.assertFalse(
                serializer.is_valid(),
                f"should not be valid if key '{key}' is missing"
            )

    def test_create_raw_event(self):
        data = {
            "event_id": "b553a92eaba94939b4e4d6725253c1c5",
            "timestamp": "2021-08-22T18:19:51.690616Z",
            "platform": "python"
        }
        serializer = RawEventSerializer(data=data)

        serializer.is_valid()
        raw_event = serializer.save(
            project_id=self.project.id,
            data=data
        )
        self.assertIsInstance(raw_event, RawEvent)
        self.assertEqual(raw_event.id, UUID(data["event_id"]))
        self.assertEqual(raw_event.project, self.project)
        self.assertEqual(raw_event.data, data)

    def test_do_not_update_raw_event(self):
        data = {
            "event_id": "b553a92eaba94939b4e4d6725253c1c5",
            "timestamp": "2021-08-22T18:19:51.690616Z",
            "platform": "python"
        }

        raw_event = RawEvent(
            id=data["event_id"],
            project_id=self.project.id,
            data=data,
        )
        raw_event.save()

        serializer = RawEventSerializer(raw_event, data=data)
        serializer.is_valid()
        self.assertRaises(
            RuntimeError,
            serializer.save,
            project_id=self.project.id,
            data=data
        )

        self.assertEqual(RawEvent.objects.count(), 1)


class EventSerializerTests(TestCase):
    def setUp(self):
        super(EventSerializerTests, self).setUp()

        self.project = Project(name="test project 1")
        self.project.save()

    def test_validate_valid_data_with_all_fields(self):
        data = {
            "event_id": "b553a92eaba94939b4e4d6725253c1c5",
            "timestamp": "2021-08-22T18:19:51.690616Z",
            "platform": "python",
            "logger": "test.logger",
            "level": "error",
            "transaction": "my-transaction",
            "environment": "develop",
            "server_name": "my-server",
            "logentry": {
                "message": "this is a log message by %s",
                "params": ["admin"]
            }
        }
        serializer = EventSerializer(data=data)

        self.assertTrue(serializer.is_valid())

    def test_validate_valid_data_with_required_fields(self):
        data = {
            "event_id": "b553a92eaba94939b4e4d6725253c1c5",
            "timestamp": "2021-08-22T18:19:51.690616Z",
            "platform": "python"
        }
        serializer = EventSerializer(data=data)

        self.assertTrue(serializer.is_valid())

    def test_validate_invalid_data_missing_required_fields(self):
        data = {
            "event_id": "b553a92eaba94939b4e4d6725253c1c5",
            "timestamp": "2021-08-22T18:19:51.690616Z",
            "platform": "python",
            "logger": "test.logger",
            "level": "error",
            "transaction": "my-transaction",
            "environment": "develop",
            "server_name": "my-server",
            "logentry": {
                "message": "this is a log message by %s",
                "params": ["admin"]
            }
        }

        for key in ["event_id", "timestamp", "platform"]:
            data_copy = data.copy()
            del data_copy[key]
            serializer = EventSerializer(data=data_copy)

            self.assertFalse(
                serializer.is_valid(),
                f"should not be valid if key '{key}' is missing"
            )

    def test_create_event_with_all_fields(self):
        data = {
            "event_id": "b553a92eaba94939b4e4d6725253c1c5",
            "timestamp": "2021-08-22T18:19:51.690616Z",
            "platform": "python",
            "logger": "test.logger",
            "level": "error",
            "transaction": "my-transaction",
            "environment": "develop",
            "server_name": "my-server",
            "logentry": {
                "message": "this is a log message by %s",
                "params": ["admin"]
            }
        }
        raw_event = RawEvent(
            id=UUID(data["event_id"]),
            project_id=self.project.id,
            data=data,
        )
        raw_event.save()

        serializer = EventSerializer(data=data)

        serializer.is_valid()
        event = serializer.save(
            raw_event=raw_event,
            project=self.project
        )
        event.save()

        self.assertIsInstance(event, Event)
        self.assertEqual(event.id, UUID(data["event_id"]))
        self.assertEqual(event.project, self.project)
        self.assertEqual(event.raw_event, raw_event)
        self.assertIsNone(event.issue)
        self.assertEqual(
            event.timestamp,
            datetime(2021, 8, 22, 18, 19, 51, 690616, tzinfo=timezone.utc)
        )
        self.assertEqual(event.platform, "python")
        self.assertEqual(event.message, "this is a log message by admin")
        self.assertEqual(event.logger, "test.logger")
        self.assertEqual(event.level, "error")
        self.assertEqual(event.transaction, "my-transaction")
        self.assertEqual(event.environment, "develop")
        self.assertEqual(event.server_name, "my-server")
        self.assertEqual(event.log_message, "this is a log message by admin")
        self.assertFalse(event.handled)
        self.assertEqual(event.mechanism, "logging")
        self.assertIsNone(event.exception_message)
        self.assertIsNone(event.runtime_name)
        self.assertIsNone(event.runtime_version)
        self.assertIsNone(event.runtime_build)
        self.assertIsNone(event.user)
        self.assertFalse(event.resolved)
        self.assertAlmostEqual(
            event.created_at,
            datetime.utcnow().replace(tzinfo=timezone.utc),
            delta=timedelta(seconds=5)
        )
        self.assertAlmostEqual(
            event.updated_at,
            datetime.utcnow().replace(tzinfo=timezone.utc),
            delta=timedelta(seconds=5)
        )
        self.assertIsNone(event.resolved_at)

    def test_create_event_with_required_fields_only(self):
        data = {
            "event_id": "b553a92eaba94939b4e4d6725253c1c5",
            "timestamp": "2021-08-22T18:19:51.690616Z",
            "platform": "python"
        }
        raw_event = RawEvent(
            id=UUID(data["event_id"]),
            project_id=self.project.id,
            data=data,
        )
        raw_event.save()

        serializer = EventSerializer(data=data)

        serializer.is_valid()
        event = serializer.save(
            raw_event=raw_event,
            project=self.project
        )
        event.save()

        self.assertIsInstance(event, Event)
        self.assertEqual(event.id, UUID(data["event_id"]))
        self.assertEqual(event.project, self.project)
        self.assertEqual(event.raw_event, raw_event)
        self.assertIsNone(event.issue)
        self.assertEqual(
            event.timestamp,
            datetime(2021, 8, 22, 18, 19, 51, 690616, tzinfo=timezone.utc)
        )
        self.assertEqual(event.platform, "python")
        self.assertEqual(
            event.message,
            "Event - b553a92eaba94939b4e4d6725253c1c5"
        )
        self.assertIsNone(event.logger)
        self.assertIsNone(event.level)
        self.assertIsNone(event.transaction)
        self.assertIsNone(event.environment)
        self.assertIsNone(event.server_name)
        self.assertIsNone(event.log_message)
        self.assertFalse(event.handled)
        self.assertIsNone(event.mechanism)
        self.assertIsNone(event.exception_message)
        self.assertIsNone(event.runtime_name)
        self.assertIsNone(event.runtime_version)
        self.assertIsNone(event.runtime_build)
        self.assertIsNone(event.user)
        self.assertFalse(event.resolved)
        self.assertAlmostEqual(
            event.created_at,
            datetime.utcnow().replace(tzinfo=timezone.utc),
            delta=timedelta(seconds=5)
        )
        self.assertAlmostEqual(
            event.updated_at,
            datetime.utcnow().replace(tzinfo=timezone.utc),
            delta=timedelta(seconds=5)
        )
        self.assertIsNone(event.resolved_at)

    def test_do_not_update_event(self):
        data = {
            "event_id": "b553a92eaba94939b4e4d6725253c1c5",
            "timestamp": "2021-08-22T18:19:51.690616Z",
            "platform": "python"
        }

        raw_event = RawEvent(
            id=UUID(data["event_id"]),
            project_id=self.project.id,
            data=data,
        )
        raw_event.save()

        event = Event(
            id=raw_event.id,
            project=self.project,
            raw_event=raw_event,
            timestamp=datetime.utcnow().replace(tzinfo=timezone.utc)
        )
        event.save()

        serializer = EventSerializer(event, data=data)
        serializer.is_valid()
        self.assertRaises(
            RuntimeError,
            serializer.save,
            raw_event=raw_event,
            project=self.project
        )

        self.assertEqual(Event.objects.count(), 1)
