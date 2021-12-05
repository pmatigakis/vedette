from uuid import uuid4

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from events.tests.factories import EventFactory


class EventDetailsTests(TestCase):
    def setUp(self):
        super(EventDetailsTests, self).setUp()
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

    def test_event_details(self):
        event = EventFactory()

        response = self.client.get(
            reverse("event-data", kwargs={"pk": event.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["object"], event)
        self.assertEqual(response.context["event"], event)
        self.assertTemplateUsed("web/events/data.html")

    def test_event_details_when_event_does_not_exist(self):
        response = self.client.get(
            reverse("event-data", kwargs={"pk": uuid4()})
        )

        self.assertEqual(response.status_code, 404)
        self.assertTemplateNotUsed("web/events/data.html")
