from django.test import TestCase

from api.signatures import calculate_event_signature


class CalculateEventSignatureTests(TestCase):
    def test_calculate_event_signature_using_message(self):
        signature = calculate_event_signature({"message": "hello world"})

        self.assertEqual(
            signature,
            "d1a6915a4417ac6dd404315e5021bdf384cc1d9103ffae5f7ca49af571aa7b1e",
        )

    def test_calculate_event_signature_using_exception(self):
        signature = calculate_event_signature(
            {"exception": {"values": [{"type": "hello world"}]}}
        )

        self.assertEqual(
            signature,
            "2e4988db616fbeaf540cfaf4bd0d7f0f2aef7813929f2bfde6259c15a24d0114",
        )

    def test_calculate_event_signature_using_logentry(self):
        signature = calculate_event_signature(
            {"logentry": {"message": "hello world"}}
        )

        self.assertEqual(
            signature,
            "91dd0b13b4cc8387fc98398448b3cdeb867de78c02f4dd8d2b232c61ed5650c6",
        )
