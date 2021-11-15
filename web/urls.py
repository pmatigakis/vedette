from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic.base import RedirectView
from rest_framework.urlpatterns import format_suffix_patterns

from .views import (
    EventDataView,
    EventDetailsView,
    EventListView,
    event_details_json,
    IssueListView,
    IssueEventsListView
)

urlpatterns = [
    path(
        "favicon.ico",
        RedirectView.as_view(url="/static/favicon.ico", permanent=True),
    ),
    path(
        "",
        RedirectView.as_view(url="/issues", permanent=True),
        name="index"
    ),
    path("issues/", IssueListView.as_view(), name="issue-list"),
    path("issues/<pk>/", IssueEventsListView.as_view(), name="issue-details"),
    path("events/", EventListView.as_view(), name="event-list"),
    path(
        "events/<event_id>.json",
        event_details_json,
        name="event-details-json"
    ),
    path("events/<pk>/", EventDetailsView.as_view(), name="event-details"),
    path("events/<pk>/data", EventDataView.as_view(), name="event-data"),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
