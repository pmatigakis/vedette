from uuid import uuid4

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from events.tests.factories import EventFactory


class EventDetailsJsonTests(TestCase):
    def setUp(self):
        super(EventDetailsJsonTests, self).setUp()
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

    def test_event_details_json(self):
        raw_event_data = {"hello": "world"}
        event = EventFactory(raw_event__data=raw_event_data)

        response = self.client.get(
            reverse("event-details-json", kwargs={"event_id": event.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, raw_event_data)

    def test_event_details_json_when_event_does_not_exist(self):
        response = self.client.get(
            reverse("event-details-json", kwargs={"event_id": uuid4()})
        )

        self.assertEqual(response.status_code, 404)
