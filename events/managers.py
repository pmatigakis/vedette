from datetime import datetime, timezone

from django.db.models import Manager

from .querysets import EventQuerySet, IssueQuerySet


class EventManager(Manager):
    def get_queryset(self):
        return EventQuerySet(self.model, using=self._db)

    def get_unresolved(self):
        return self.get_queryset().get_unresolved()

    def resolve_by_issue(self, issue):
        self.get_queryset().get_by_issue(issue.id).update(
            resolved=True,
            resolved_at=datetime.utcnow().replace(tzinfo=timezone.utc),
        )


class IssueManager(Manager):
    def get_queryset(self):
        return IssueQuerySet(self.model, using=self._db)

    def get_unresolved(self):
        return self.get_queryset().get_unresolved()
