from django.db.models.query import QuerySet


class EventQuerySet(QuerySet):
    def get_unresolved(self):
        return self.filter(resolved=False)

    def get_event(self, event_id):
        return self.filter(id=event_id)


class IssueQuerySet(QuerySet):
    def get_unresolved(self):
        return self.filter(resolved=False)
