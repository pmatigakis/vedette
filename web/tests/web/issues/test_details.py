from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from events.tests.factories import EventFactory


class IssueDetailsTests(TestCase):
    def setUp(self):
        super(IssueDetailsTests, self).setUp()
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

    def test_issue_details(self):
        event = EventFactory()

        response = self.client.get(
            reverse("issue-details", kwargs={"pk": event.issue.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["issue"], event.issue)
        self.assertQuerysetEqual(response.context["object_list"], [event])
        self.assertTemplateUsed("web/issues/details.html")

    def test_issue_details_with_unknown_issue(self):
        response = self.client.get(reverse("issue-details", kwargs={"pk": 1}))

        self.assertEqual(response.status_code, 404)
        self.assertTemplateNotUsed("web/issues/details.html")
