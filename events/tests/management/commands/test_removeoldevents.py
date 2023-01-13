from datetime import datetime, timedelta, timezone
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from freezegun import freeze_time

from events.models import RawEvent
from events.tests.factories import EventFactory, RawEventFactory


class RemoveOldEventsTests(TestCase):
    @freeze_time("2021-12-01")
    def test_run_command_when_there_are_no_events(self):
        out = StringIO()
        call_command("removeoldevents", "--days=3", stdout=out)

        self.assertIn(
            "Deleted 0 events before 2021-11-28 00:00:00+00:00\n",
            out.getvalue(),
        )

    @freeze_time("2021-12-01")
    def test_run_command(self):
        current_datetime = datetime(2021, 12, 1, tzinfo=timezone.utc)
        raw_events = []
        for i in range(7):
            raw_event = RawEventFactory()
            raw_event.created_at = current_datetime - timedelta(days=i)
            raw_event.save()
            raw_events.append(raw_event)

        out = StringIO()
        call_command("removeoldevents", "--days=3", stdout=out)

        self.assertCountEqual(RawEvent.objects.all(), raw_events[0:3])

        self.assertIn(
            "Deleted 4 events before 2021-11-28 00:00:00+00:00\n",
            out.getvalue(),
        )

    @freeze_time("2021-12-01")
    def test_run_command_with_default_arguments(self):
        current_datetime = datetime(2021, 12, 1, tzinfo=timezone.utc)
        raw_events = []
        for i in range(14):
            raw_event = RawEventFactory()
            raw_event.created_at = current_datetime - timedelta(days=i)
            raw_event.save()
            raw_events.append(raw_event)

        out = StringIO()
        call_command("removeoldevents", stdout=out)

        self.assertCountEqual(list(RawEvent.objects.all()), raw_events[0:7])

        self.assertIn(
            "Deleted 7 events before 2021-11-24 00:00:00+00:00\n",
            out.getvalue(),
        )

    @freeze_time("2021-12-01")
    def test_run_command_only_deletes_raw_events_without_primary_events(self):
        current_datetime = datetime(2021, 12, 1, tzinfo=timezone.utc)
        primary_event_1 = EventFactory()
        primary_event_1.created_at = current_datetime - timedelta(days=7)
        primary_event_1.save()
        primary_event_1.raw_event.created_at = primary_event_1.created_at
        primary_event_1.raw_event.save()
        extra_event = EventFactory(issue=primary_event_1.issue)
        extra_event.created_at = current_datetime - timedelta(days=7)
        extra_event.save()
        extra_event.raw_event.created_at = extra_event.created_at
        extra_event.raw_event.save()

        out = StringIO()
        call_command("removeoldevents", "--days=3", stdout=out)

        self.assertCountEqual(
            RawEvent.objects.all(), [primary_event_1.raw_event]
        )

        self.assertIn(
            "Deleted 2 events before 2021-11-28 00:00:00+00:00\n",
            out.getvalue(),
        )
