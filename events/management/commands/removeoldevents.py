from datetime import datetime, timedelta, timezone

from django.core.management.base import BaseCommand, CommandError

from events.models import RawEvent


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            help="Delete events before those number of days",
            type=int,
            default=7,
        )

    def handle(self, *args, **options):
        days = options["days"]
        if days <= 0:
            raise CommandError("Give a number of days greater than 0")

        before_date = datetime.utcnow().replace(
            tzinfo=timezone.utc
        ) - timedelta(days=days)
        qs = RawEvent.objects.filter(created_at__lte=before_date)
        self.stdout.write(
            f"Deleting {qs.count()} events before "
            f"{before_date.isoformat(sep=' ')}"
        )

        qs.delete()
