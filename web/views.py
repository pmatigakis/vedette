from django.http import JsonResponse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from events.models import RawEvent, Event


class EventListView(LoginRequiredMixin, ListView):
    model = Event
    paginate_by = 10
    template_name = "web/events/list.html"
    ordering = ["-timestamp"]


class EventDetailsView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = "web/events/details.html"


@login_required
def event_details_json(request, event_id):
    raw_event = get_object_or_404(RawEvent, pk=event_id)

    return JsonResponse(raw_event.data)
