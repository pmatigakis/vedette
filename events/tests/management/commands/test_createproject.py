from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from events.models import Project
from events.tests.factories import ProjectFactory


class CreateProjectTests(TestCase):
    def test_create_project(self):
        out = StringIO()
        call_command("createproject", "test-project", stdout=out)

        projects = Project.objects.all()
        self.assertEqual(len(projects), 1)
        self.assertIn(
            f"Project id: {projects[0].id}\n",
            out.getvalue(),
        )
        self.assertIn(
            "Project name: test-project\n",
            out.getvalue(),
        )
        self.assertIn(
            f"Project public key: {projects[0].public_key}\n",
            out.getvalue(),
        )

    def test_create_project_does_not_create_project_with_duplicate_same(self):
        ProjectFactory(name="test-project")

        out = StringIO()
        with self.assertRaises(CommandError) as e:
            call_command("createproject", "test-project", stdout=out)
        self.assertEqual(
            e.exception.args,
            ("A project with the name 'test-project' already exists",),
        )

        projects = Project.objects.all()
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].name, "test-project")
