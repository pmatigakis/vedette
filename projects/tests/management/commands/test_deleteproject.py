from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from projects.models import Project
from projects.tests.factories import ProjectFactory


class DeleteProjectTests(TestCase):
    def test_delete_project(self):
        project_1 = ProjectFactory()
        project_2 = ProjectFactory()

        out = StringIO()
        call_command("deleteproject", project_1.name, stdout=out)

        self.assertIn(
            f"Deleted project with name {project_1.name}",
            out.getvalue(),
        )

        self.assertFalse(Project.objects.filter(pk=project_1.id).exists())
        self.assertTrue(Project.objects.filter(pk=project_2.id).exists())

    def test_delete_project_does_Nothing_hen_project_does_not_exist(self):
        project_1 = ProjectFactory()

        out = StringIO()
        with self.assertRaises(CommandError) as e:
            call_command("deleteproject", "unknown-project", stdout=out)
        self.assertEqual(
            e.exception.args,
            ("A project with the name 'unknown-project' doesn't exist",),
        )

        self.assertTrue(Project.objects.filter(pk=project_1.id).exists())
