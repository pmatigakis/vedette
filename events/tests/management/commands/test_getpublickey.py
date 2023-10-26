from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from events.tests.factories import ProjectFactory


class GetPublicKeyTests(TestCase):
    def test_get_public_key(self):
        project = ProjectFactory()

        out = StringIO()
        call_command("getpublickey", project.name, stdout=out)

        self.assertIn(
            f"Project public key: {project.public_key}\n",
            out.getvalue(),
        )

    def test_get_public_key_when_project_does_not_exist(self):
        out = StringIO()
        with self.assertRaises(CommandError) as e:
            call_command("getpublickey", "unknown-project", stdout=out)
        self.assertEqual(
            e.exception.args,
            ("A project with the name 'unknown-project' doesn't exist",),
        )
