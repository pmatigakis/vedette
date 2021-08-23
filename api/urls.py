from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import StoreEvent

urlpatterns = [
    path('<int:project_id>/store/', StoreEvent.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
