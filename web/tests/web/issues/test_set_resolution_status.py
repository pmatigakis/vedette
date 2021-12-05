from datetime import datetime, timedelta, timezone

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from events.tests.factories import EventFactory


class SetResolutionStatusTests(TestCase):
    def setUp(self):
        super(SetResolutionStatusTests, self).setUp()
        self.username = "admin"
        self.password = "admin"

        user = User.objects.create_user(
            username=self.username, password=self.password
        )
        user.save()

        self.client = Client()
        response = self.client.post(
            reverse("login"),
            {"username": self.username, "password": self.password},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

    def test_mark_event_as_resolved(self):
        event = EventFactory()
        event_to_remain_unresolved = EventFactory()

        response = self.client.get(
            reverse(
                "issue-set-resolution-status",
                kwargs={"issue_id": event.issue.id},
            ),
            {"resolved": "true"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response, reverse("issue-details", kwargs={"pk": event.issue.id})
        )
        self.assertEqual(response.context["issue"], event.issue)
        self.assertQuerysetEqual(response.context["object_list"], [event])
        self.assertTemplateUsed("web/issue/details.html")

        event.refresh_from_db()
        self.assertTrue(event.resolved)
        self.assertAlmostEqual(
            event.resolved_at,
            datetime.utcnow().replace(tzinfo=timezone.utc),
            delta=timedelta(seconds=3),
        )

        self.assertTrue(event.issue.resolved)
        self.assertAlmostEqual(
            event.issue.resolved_at,
            datetime.utcnow().replace(tzinfo=timezone.utc),
            delta=timedelta(seconds=3),
        )

        event_to_remain_unresolved.refresh_from_db()
        self.assertFalse(event_to_remain_unresolved.resolved)
        self.assertIsNone(event_to_remain_unresolved.resolved_at)
        self.assertFalse(event_to_remain_unresolved.issue.resolved)
        self.assertIsNone(event_to_remain_unresolved.issue.resolved_at)

    def test_mark_issue_as_unresolved(self):
        resolved_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        event = EventFactory(resolved=True, resolved_at=resolved_at)
        event_to_remain_resolved = EventFactory(
            resolved=True,
            resolved_at=resolved_at,
            issue__resolved=True,
            issue__resolved_at=resolved_at,
        )

        response = self.client.get(
            reverse(
                "issue-set-resolution-status",
                kwargs={"issue_id": event.issue.id},
            ),
            {"resolved": "false"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response, reverse("issue-details", kwargs={"pk": event.issue.id})
        )
        self.assertQuerysetEqual(response.context["object_list"], [event])
        self.assertEqual(response.context["issue"], event.issue)
        self.assertTemplateUsed("web/issues/details.html")

        event.refresh_from_db()
        self.assertTrue(event.resolved)
        self.assertAlmostEqual(
            event.resolved_at,
            resolved_at,
            delta=timedelta(seconds=3),
        )
        self.assertFalse(event.issue.resolved)
        self.assertIsNone(event.issue.resolved_at)

        event_to_remain_resolved.refresh_from_db()
        self.assertTrue(event_to_remain_resolved.resolved)
        self.assertAlmostEqual(
            event_to_remain_resolved.resolved_at,
            resolved_at,
            delta=timedelta(seconds=3),
        )
        self.assertTrue(event_to_remain_resolved.issue.resolved)
        self.assertAlmostEqual(
            event_to_remain_resolved.issue.resolved_at,
            resolved_at,
            delta=timedelta(seconds=3),
        )

    def test_mark_issue_resolution_with_invalid_status(self):
        event = EventFactory()

        response = self.client.get(
            reverse(
                "issue-set-resolution-status",
                kwargs={"issue_id": event.issue.id},
            ),
            {"resolved": "hello-world"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertTemplateNotUsed("web/issues/details.html")

    def test_mark_issue_resolution_with_missing_resolution_status(self):
        event = EventFactory()

        response = self.client.get(
            reverse(
                "issue-set-resolution-status",
                kwargs={"issue_id": event.issue.id},
            )
        )
        self.assertEqual(response.status_code, 400)
        self.assertTemplateNotUsed("web/issues/details.html")

    def test_mark_issue_with_invalid_issue_id(self):
        response = self.client.get(
            reverse("issue-set-resolution-status", kwargs={"issue_id": 1}),
            {"resolved": "true"},
            follow=True,
        )
        self.assertEqual(response.status_code, 404)
        self.assertTemplateNotUsed("web/issue/details.html")
