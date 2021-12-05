from datetime import datetime, timedelta, timezone

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from events.models import Event
from events.tests.factories import EventFactory


class EventListTests(TestCase):
    def setUp(self):
        super(EventListTests, self).setUp()
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

    def test_list_events_when_there_are_no_events(self):
        response = self.client.get(reverse("event-list"))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["object_list"], [])
        self.assertFalse(response.context["page_obj"].has_previous())
        self.assertFalse(response.context["page_obj"].has_next())
        self.assertEqual(response.context["page_obj"].number, 1)
        self.assertTemplateUsed("web/events/list.html")

    def test_list_events(self):
        EventFactory()

        response = self.client.get(reverse("event-list"))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context["object_list"], list(Event.objects.all())
        )
        self.assertFalse(response.context["page_obj"].has_previous())
        self.assertFalse(response.context["page_obj"].has_next())
        self.assertEqual(response.context["page_obj"].number, 1)
        self.assertTemplateUsed("web/events/list.html")

    def test_list_events_does_not_show_resolved_events(self):
        EventFactory(
            resolved=True,
            resolved_at=datetime.utcnow().replace(tzinfo=timezone.utc),
        )
        event = EventFactory()

        response = self.client.get(reverse("event-list"))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["object_list"], [event])
        self.assertFalse(response.context["page_obj"].has_previous())
        self.assertFalse(response.context["page_obj"].has_next())
        self.assertEqual(response.context["page_obj"].number, 1)
        self.assertTemplateUsed("web/events/list.html")

    def test_list_event_pagination(self):
        current_time = datetime.utcnow().replace(tzinfo=timezone.utc)

        events = [
            EventFactory(timestamp=current_time - timedelta(seconds=i))
            for i in range(30)
        ]

        response = self.client.get(reverse("event-list"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["object_list"], events[0:10])
        self.assertFalse(response.context["page_obj"].has_previous())
        self.assertTrue(response.context["page_obj"].has_next())
        self.assertEqual(response.context["page_obj"].number, 1)
        self.assertTemplateUsed("web/events/list.html")

        response = self.client.get(reverse("event-list"), {"page": 2})
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context["object_list"], events[10:20]
        )
        self.assertTrue(response.context["page_obj"].has_previous())
        self.assertTrue(response.context["page_obj"].has_next())
        self.assertEqual(response.context["page_obj"].number, 2)
        self.assertTemplateUsed("web/events/list.html")

        response = self.client.get(reverse("event-list"), {"page": 3})
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context["object_list"], events[20:30]
        )
        self.assertTrue(response.context["page_obj"].has_previous())
        self.assertFalse(response.context["page_obj"].has_next())
        self.assertEqual(response.context["page_obj"].number, 3)
        self.assertTemplateUsed("web/events/list.html")

    def test_list_event_pagination_with_invalid_page_number(self):
        EventFactory()

        response = self.client.get(reverse("event-list"), {"page": 10000})

        self.assertEqual(response.status_code, 404)
        self.assertNotIn("object_list", response.context)
        self.assertNotIn("page_obj", response.context)
        self.assertTemplateNotUsed("web/events/list.html")
