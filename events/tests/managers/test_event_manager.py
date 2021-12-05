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
        event_to_resolve = EventFactory()
        event_to_remain_resolved = EventFactory()

        Event.objects.resolve(event_to_resolve)

        event_to_resolve.refresh_from_db()
        event_to_remain_resolved.refresh_from_db()

        self.assertTrue(event_to_resolve.resolved)
        self.assertAlmostEqual(
            event_to_resolve.resolved_at,
            datetime.utcnow().replace(tzinfo=timezone.utc),
            delta=timedelta(seconds=3),
        )

        self.assertFalse(event_to_remain_resolved.resolved)
        self.assertIsNone(event_to_remain_resolved.resolved_at)

    def test_unresolve(self):
        resolved_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        event_to_unresolve = EventFactory(
            resolved=True,
            resolved_at=resolved_at,
        )

        event_to_remain_resolved = EventFactory(
            resolved=True,
            resolved_at=resolved_at,
        )

        Event.objects.unresolve(event_to_unresolve)

        event_to_unresolve.refresh_from_db()
        event_to_remain_resolved.refresh_from_db()

        self.assertFalse(event_to_unresolve.resolved)
        self.assertIsNone(event_to_unresolve.resolved_at)

        self.assertTrue(event_to_remain_resolved.resolved)
        self.assertEqual(event_to_remain_resolved.resolved_at, resolved_at)

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
