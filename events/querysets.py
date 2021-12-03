from django.db.models.query import QuerySet


class EventQuerySet(QuerySet):
    def get_unresolved(self):
        return self.filter(resolved=False)

    def get_event(self, event_id):
        return self.filter(id=event_id)

    def get_by_issue(self, issue_id):
        return self.filter(issue_id=issue_id)


class IssueQuerySet(QuerySet):
    def get_unresolved(self):
        return self.filter(resolved=False)

    def get_issue(self, issue_id):
        return self.filter(id=issue_id)
