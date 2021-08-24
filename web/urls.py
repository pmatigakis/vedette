from django.urls import path
from django.contrib.auth import views as auth_views
from rest_framework.urlpatterns import format_suffix_patterns

from .views import EventListView, EventDetailsView, event_details_json

urlpatterns = [
    path('', EventListView.as_view(), name="event-list"),
    path('<event_id>.json', event_details_json, name='event-details-json'),
    path('<pk>/', EventDetailsView.as_view(), name='event-details'),
    path('accounts/login/', auth_views.LoginView.as_view(), name="login"),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name="logout"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
