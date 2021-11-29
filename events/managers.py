from django.db.models import Manager

from .querysets import EventQuerySet


class EventManager(Manager):
    def get_queryset(self):
        return EventQuerySet(self.model, using=self._db)
