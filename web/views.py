from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from events.models import Event, Issue, RawEvent


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
        issue = get_object_or_404(Issue, pk=self.kwargs["pk"])

        return super(IssueEventsListView, self).get_context_data(
            object_list=object_list, issue=issue, **kwargs
        )


def set_event_resolution_status(request, event_id):
    resolved = request.GET.get("resolved")
    if not resolved:
        return HttpResponseBadRequest()

    resolved = resolved.lower()
    if resolved not in ["true", "false"]:
        return HttpResponseBadRequest()

    event = get_object_or_404(Event, pk=event_id)
    if resolved == "true":
        event.resolve()
    else:
        event.unresolve()

    event.save()

    return redirect("event-details", pk=event.id)


def set_issue_resolution_status(request, issue_id):
    resolved = request.GET.get("resolved")
    if not resolved:
        return HttpResponseBadRequest()

    resolved = resolved.lower()
    if resolved not in ["true", "false"]:
        return HttpResponseBadRequest()

    issue = get_object_or_404(Issue, pk=issue_id)
    if resolved == "true":
        with transaction.atomic():
            issue.resolve()
            issue.save()
            Event.objects.resolve_by_issue(issue)
    else:
        issue.unresolve()
        issue.save()

    return redirect("issue-details", pk=issue.id)
