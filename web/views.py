from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from events.models import Event, RawEvent, Issue


class EventListView(LoginRequiredMixin, ListView):
    model = Event
    paginate_by = 10
    template_name = "web/events/list.html"
    ordering = ["-timestamp"]
    queryset = Event.objects.get_unresolved()


class EventDetailsView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = "web/events/details.html"


class EventDataView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = "web/events/data.html"


@login_required
def event_details_json(request, event_id):
    raw_event = get_object_or_404(RawEvent, pk=event_id)

    return JsonResponse(raw_event.data)


class IssueListView(LoginRequiredMixin, ListView):
    model = Issue
    paginate_by = 10
    template_name = "web/issues/list.html"
    ordering = ["-last_seen_at"]
    queryset = Issue.objects.get_unresolved()


class IssueEventsListView(LoginRequiredMixin, ListView):
    model = Event
    paginate_by = 10
    template_name = "web/issues/details.html"
    ordering = ["-timestamp"]

    def get_queryset(self):
        queryset = super(IssueEventsListView, self).get_queryset()

        return queryset.filter(issue_id=self.kwargs["pk"])

    def get_context_data(self, *, object_list=None, **kwargs):
        issue = Issue.objects.get(pk=self.kwargs["pk"])

        return super(IssueEventsListView, self).get_context_data(
            object_list=object_list,
            issue=issue,
            **kwargs
        )
