from datetime import datetime, timezone

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
