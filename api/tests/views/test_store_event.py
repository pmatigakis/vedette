from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from projects.models import Project


class StoreEventTests(TestCase):
    def setUp(self):
        super(StoreEventTests, self).setUp()

        project = Project(name="test project")
        project.save()
        self.project_id = project.id

    @patch("api.views.capture_event.apply_async")
    def test_store_event_requires_authentication(
        self, capture_event_apply_async_mock
    ):
        client = APIClient()
        response = client.post(
            f"/api/{self.project_id}/store/",
            {
                "event_id": "5d167e7d21004858ae9dfba46d370377",
                "timestamp": "2021-08-22T18:26:04.994971Z",
                "platform": "python",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"detail": "missing authentication"})

        capture_event_apply_async_mock.assert_not_called()

    @patch("api.views.capture_event.apply_async")
    def test_store_event_requires_valid_authentication(
        self, capture_event_apply_async_mock
    ):
        client = APIClient()
        client.credentials(HTTP_X_SENTRY_AUTH="invalid-authentication")

        response = client.post(
            f"/api/{self.project_id}/store/",
            {
                "event_id": "5d167e7d21004858ae9dfba46d370377",
                "timestamp": "2021-08-22T18:26:04.994971Z",
                "platform": "python",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"detail": "missing authentication"})

        capture_event_apply_async_mock.assert_not_called()

    @patch("api.views.capture_event.apply_async")
    def test_store_event_requires_valid_sentry_key(
        self, capture_event_apply_async_mock
    ):
        client = APIClient()
        client.credentials(
            HTTP_X_SENTRY_AUTH="Sentry "
            "sentry_version=7, "
            "sentry_client=sentry.python/1.1.0"
        )

        response = client.post(
            f"/api/{self.project_id}/store/",
            {
                "event_id": "5d167e7d21004858ae9dfba46d370377",
                "timestamp": "2021-08-22T18:26:04.994971Z",
                "platform": "python",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"detail": "missing public key"})

        capture_event_apply_async_mock.assert_not_called()

    @patch("api.views.capture_event.apply_async")
    def test_store_event(self, capture_event_apply_async_mock):
        client = APIClient()
        client.credentials(
            HTTP_X_SENTRY_AUTH="Sentry sentry_key=PublicKey, "
            "sentry_version=7, "
            "sentry_client=sentry.python/1.1.0"
        )

        response = client.post(
            f"/api/{self.project_id}/store/",
            {
                "event_id": "5d167e7d21004858ae9dfba46d370377",
                "timestamp": "2021-08-22T18:26:04.994971Z",
                "platform": "python",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"message": "the event has been received"}
        )

        capture_event_apply_async_mock.assert_called_once()

    @patch("api.views.capture_event.apply_async")
    def test_store_event_rejects_event_with_missing_attribute(
        self, capture_event_apply_async_mock
    ):
        event = {
            "event_id": "5d167e7d21004858ae9dfba46d370377",
            "timestamp": "2021-08-22T18:26:04.994971Z",
            "platform": "python",
        }

        client = APIClient()
        client.credentials(
            HTTP_X_SENTRY_AUTH="Sentry sentry_key=PublicKey, "
            "sentry_version=7, "
            "sentry_client=sentry.python/1.1.0"
        )

        for missing_attribute in event.keys():
            new_event = event.copy()
            del new_event[missing_attribute]

            response = client.post(
                f"/api/{self.project_id}/store/", new_event, format="json"
            )

            self.assertEqual(
                response.status_code,
                400,
                f"the attribute {missing_attribute} is not missing in "
                f"the request body",
            )

            self.assertEqual(
                response.json(), {"message": "invalid event payload"}
            )

        capture_event_apply_async_mock.assert_not_called()
