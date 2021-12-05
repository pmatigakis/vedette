from datetime import datetime, timedelta, timezone

from django.test import TestCase

from events.models import Event
from events.querysets import EventQuerySet
from events.tests.factories import EventFactory


class EventManagerTests(TestCase):
    def test_get_queryset(self):
        self.assertIsInstance(Event.objects.get_queryset(), EventQuerySet)

    def test_get_unresolved(self):
        EventFactory(
            resolved=True,
            resolved_at=datetime.utcnow().replace(tzinfo=timezone.utc),
        )
        unresolved_event = EventFactory()

        self.assertEqual(
            list(Event.objects.get_unresolved()), [unresolved_event]
        )

    def test_resolve(self):
        event = EventFactory()
        self.assertFalse(event.resolved)
        self.assertIsNone(event.resolved_at)

        Event.objects.resolve(event)

        event.refresh_from_db()
        self.assertTrue(event.resolved)
        self.assertAlmostEqual(
            event.resolved_at,
            datetime.utcnow().replace(tzinfo=timezone.utc),
            delta=timedelta(seconds=3),
        )

    def test_unresolve(self):
        event = EventFactory(
            resolved=True,
            resolved_at=datetime.utcnow().replace(tzinfo=timezone.utc),
        )

        Event.objects.unresolve(event)

        event.refresh_from_db()
        self.assertFalse(event.resolved)
        self.assertIsNone(event.resolved_at)

    def test_resolve_by_issue(self):
        event_1 = EventFactory()
        event_2 = EventFactory()

        self.assertFalse(event_1.resolved)
        self.assertIsNone(event_1.resolved_at)
        self.assertFalse(event_2.resolved)
        self.assertIsNone(event_2.resolved_at)

        Event.objects.resolve_by_issue(event_1.issue)

        event_1.refresh_from_db()
        event_1.refresh_from_db()

        self.assertTrue(event_1.resolved)
        self.assertAlmostEqual(
            event_1.resolved_at,
            datetime.utcnow().replace(tzinfo=timezone.utc),
            delta=timedelta(seconds=3),
        )

        self.assertFalse(event_2.resolved)
        self.assertIsNone(event_2.resolved_at)
