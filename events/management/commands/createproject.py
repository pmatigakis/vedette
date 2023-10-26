from django.core.management.base import BaseCommand, CommandError

from events.models import Project


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("project-name", help="The project name")

    def handle(self, *args, **options):
        name = options["project-name"]
        self.stdout.write(f"Creating project {name}")

        if Project.objects.filter(name=name).exists():
            raise CommandError(
                f"A project with the name '{name}' already exists"
            )

        project = Project(name=name)
        project.save()

        self.stdout.write(f"Project id: {project.id}")
        self.stdout.write(f"Project name: {project.name}")
        self.stdout.write(f"Project public key: {project.public_key}")
