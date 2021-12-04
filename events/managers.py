from datetime import datetime, timezone

from django.db.models import Manager

from .querysets import EventQuerySet, IssueQuerySet


class EventManager(Manager):
    def get_queryset(self):
        return EventQuerySet(self.model, using=self._db)

    def get_unresolved(self):
        return self.get_queryset().get_unresolved()

    def resolve(self, event):
        self.get_queryset().get_event(event.id).update(
            resolved=True,
            resolved_at=datetime.utcnow().replace(tzinfo=timezone.utc),
        )

    def resolve_by_issue(self, issue):
        self.get_queryset().get_by_issue(issue.id).update(
            resolved=True,
            resolved_at=datetime.utcnow().replace(tzinfo=timezone.utc),
        )

    def unresolve(self, event):
        self.get_queryset().get_event(event.id).update(
            resolved=False, resolved_at=None
        )


class IssueManager(Manager):
    def get_queryset(self):
        return IssueQuerySet(self.model, using=self._db)

    def get_unresolved(self):
        return self.get_queryset().get_unresolved()

    def resolve(self, issue):
        self.get_queryset().get_issue(issue.id).update(
            resolved=True,
            resolved_at=datetime.utcnow().replace(tzinfo=timezone.utc),
        )

    def unresolve(self, issue):
        self.get_queryset().get_issue(issue.id).update(
            resolved=False, resolved_at=None
        )
