from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic.base import RedirectView
from rest_framework.urlpatterns import format_suffix_patterns

from .views import (
    EventDataView,
    EventDetailsView,
    EventListView,
    IssueEventsListView,
    IssueListView,
    event_details_json,
    search,
    set_event_resolution_status,
    set_issue_resolution_status,
)

urlpatterns = [
    path(
        "favicon.ico",
        RedirectView.as_view(url="/static/favicon.ico", permanent=True),
    ),
    path(
        "", RedirectView.as_view(url="/issues", permanent=True), name="index"
    ),
    path("issues/", IssueListView.as_view(), name="issue-list"),
    path(
        "issues/<int:pk>/", IssueEventsListView.as_view(), name="issue-details"
    ),
    path(
        "issues/<int:issue_id>/resolution",
        set_issue_resolution_status,
        name="issue-set-resolution-status",
    ),
    path("events/", EventListView.as_view(), name="event-list"),
    path(
        "events/<uuid:event_id>.json",
        event_details_json,
        name="event-details-json",
    ),
    path(
        "events/<uuid:pk>/", EventDetailsView.as_view(), name="event-details"
    ),
    path(
        "events/<uuid:event_id>/resolution",
        set_event_resolution_status,
        name="event-set-resolution-status",
    ),
    path("events/uuid:<pk>/data", EventDataView.as_view(), name="event-data"),
    path("search", search, name="search"),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
