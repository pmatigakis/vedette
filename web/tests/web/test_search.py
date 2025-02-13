from django.contrib.auth.models import User
from django.test import Client, TransactionTestCase
from django.urls import reverse

from events.tests.factories import EventFactory


class SearchTests(TransactionTestCase):
    def setUp(self):
        super(SearchTests, self).setUp()
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

    def test_search_when_there_are_no_events(self):
        response = self.client.get(reverse("search"), {"query": "hello world"})
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["object_list"], [])
        self.assertFalse(response.context["page_obj"].has_previous())
        self.assertFalse(response.context["page_obj"].has_next())
        self.assertEqual(response.context["page_obj"].number, 1)
        self.assertTemplateUsed("web/search.html")

    def test_search(self):
        event_2 = EventFactory(message="hello world")
        event_1 = EventFactory(message="hello world first")
        irrelevant_event = EventFactory(message="this is a test")

        response = self.client.get(reverse("search"), {"query": "hello"})

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["object_list"],
            # [issue_2, issue_1, irrelevant_issue],
            [event_2.issue, event_1.issue, irrelevant_event.issue],
        )

        self.assertFalse(response.context["page_obj"].has_previous())
        self.assertFalse(response.context["page_obj"].has_next())
        self.assertEqual(response.context["page_obj"].number, 1)
        self.assertTemplateUsed("web/issues/list.html")
