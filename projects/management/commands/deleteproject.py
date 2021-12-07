from django.core.management.base import BaseCommand, CommandError

from projects.models import Project


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("project-name", help="The project name")

    def handle(self, *args, **options):
        name = options["project-name"]

        try:
            project = Project.objects.get(name=name)
        except Project.DoesNotExist:
            raise CommandError(
                f"A project with the name '{name}' doesn't exist"
            )

        project.delete()
        self.stdout.write(f"Deleted project with name {project.name}")
