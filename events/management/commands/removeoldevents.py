from datetime import datetime, timedelta, timezone
from itertools import islice

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from events.models import Issue, RawEvent


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

        primary_event_query = Issue.objects.exclude(
            primary_event__isnull=True
        ).values_list("primary_event", flat=True)

        qs = (
            RawEvent.objects.values_list("pk")
            .exclude(
                Q(event__in=primary_event_query)
                | Q(created_at__gt=before_date)
            )
            .iterator()
        )

        deleted_raw_event_count = 0
        while True:
            raw_event_ids = [item[0] for item in list(islice(qs, 100))]
            if not raw_event_ids:
                break

            raw_events_deleted, _ = RawEvent.objects.filter(
                pk__in=raw_event_ids
            ).delete()
            deleted_raw_event_count += raw_events_deleted

        self.stdout.write(
            f"Deleted {deleted_raw_event_count} events before "
            f"{before_date.isoformat(sep=' ')}"
        )
