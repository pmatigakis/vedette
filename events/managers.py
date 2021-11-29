from django.db.models import Manager

from .querysets import EventQuerySet, IssueQuerySet


class EventManager(Manager):
    def get_queryset(self):
        return EventQuerySet(self.model, using=self._db)


class IssueManager(Manager):
    def get_queryset(self):
        return IssueQuerySet(self.model, using=self._db)
