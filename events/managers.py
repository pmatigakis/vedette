from django.db.models import Manager

from .querysets import EventQuerySet, IssueQuerySet


class EventManager(Manager):
    def get_queryset(self):
        return EventQuerySet(self.model, using=self._db)

    def get_unresolved(self):
        return self.get_queryset().get_unresolved()


class IssueManager(Manager):
    def get_queryset(self):
        return IssueQuerySet(self.model, using=self._db)

    def get_unresolved(self):
        return self.get_queryset().get_unresolved()
