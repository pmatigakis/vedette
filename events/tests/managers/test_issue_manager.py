from datetime import datetime, timedelta, timezone

from django.test import TestCase

from events.models import Issue
from events.querysets import IssueQuerySet
from events.tests.factories import IssueFactory


class IssueManagerTests(TestCase):
    def test_get_queryset(self):
        self.assertIsInstance(Issue.objects.get_queryset(), IssueQuerySet)

    def test_get_unresolved(self):
        IssueFactory(
            resolved=True,
            resolved_at=datetime.utcnow().replace(tzinfo=timezone.utc),
        )

        unresolved_issue = IssueFactory()

        self.assertEqual(
            list(Issue.objects.get_unresolved()), [unresolved_issue]
        )

    def test_resolve(self):
        issue_to_resolve = IssueFactory()
        issue_to_remain_unresolved = IssueFactory()

        Issue.objects.resolve(issue_to_resolve)

        issue_to_resolve.refresh_from_db()
        self.assertTrue(issue_to_resolve.resolved)
        self.assertAlmostEqual(
            issue_to_resolve.resolved_at,
            datetime.utcnow().replace(tzinfo=timezone.utc),
            delta=timedelta(seconds=3),
        )

        issue_to_remain_unresolved.refresh_from_db()
        self.assertFalse(issue_to_remain_unresolved.resolved)
        self.assertIsNone(issue_to_remain_unresolved.resolved_at)

    def test_unresolve(self):
        resolved_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        issue_to_unresolve = IssueFactory(
            resolved=True, resolved_at=resolved_at
        )

        issue_to_remain_resolved = IssueFactory(
            resolved=True, resolved_at=resolved_at
        )

        Issue.objects.unresolve(issue_to_unresolve)

        issue_to_unresolve.refresh_from_db()
        issue_to_remain_resolved.refresh_from_db()

        self.assertFalse(issue_to_unresolve.resolved)
        self.assertIsNone(issue_to_unresolve.resolved_at)

        self.assertTrue(issue_to_remain_resolved.resolved)
        self.assertEqual(issue_to_remain_resolved.resolved_at, resolved_at)
