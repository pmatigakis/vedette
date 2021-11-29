from django.db.models.query import QuerySet


class EventQuerySet(QuerySet):
    def get_unresolved(self):
        return self.filter(resolved=False)
