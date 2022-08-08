from datetime import datetime, timedelta, timezone

from django.test import TestCase

from events.tests.factories import IssueFactory


class IssueTests(TestCase):
    def test_resolve(self):
        issue = IssueFactory()
        issue.resolve()
        issue.save()

        self.assertTrue(issue.resolved)
        self.assertGreaterEqual(issue.resolved_at, issue.created_at)
        self.assertAlmostEqual(
            issue.resolved_at,
            datetime.now(tz=timezone.utc),
            delta=timedelta(seconds=3),
        )

    def test_unresolve(self):
        issue = IssueFactory(resolved_at=datetime.now(), resolved=True)
        issue.unresolve()
        issue.save()

        self.assertFalse(issue.resolved)
        self.assertIsNone(issue.resolved_at)
