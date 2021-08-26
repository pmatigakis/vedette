from uuid import UUID

from rest_framework.exceptions import PermissionDenied, NotAuthenticated, NotFound
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer

from events.models import Event
from events.negotiation import IgnoreClientContentNegotiation
from events.parsers import GzippedJSONParser
from projects.models import Project

from .serializers import EventSerializer


class StoreEvent(APIView):
    parser_classes = [GzippedJSONParser]
    renderer_classes = [JSONRenderer]
    content_negotiation_class = IgnoreClientContentNegotiation

    def _authenticate(self, request, project_id):
        if "HTTP_X_SENTRY_AUTH" not in request.META:
            raise NotAuthenticated(detail="missing authentication")

        auth_components = request.META["HTTP_X_SENTRY_AUTH"].split(" ", 1)
        if len(auth_components) != 2:
            raise NotAuthenticated(detail="missing authentication")

        public_key = None
        for authentication_component in auth_components[1].split(","):
            auth_values = authentication_component.split("=")
            if len(auth_values) == 2:
                key = auth_values[0].strip()
                if key == "sentry_key":
                    try:
                        public_key = UUID(auth_values[1].strip())
                    except ValueError:
                        raise NotAuthenticated(detail="invalid authentication")
                    break

        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            raise NotFound(detail="the requested project doesn't exist")

        if project.public_key != public_key:
            raise PermissionDenied(detail="invalid authentication")

    def _process_event(self, project_id, serializer, event_data):
        if Event.objects.filter(
                id=serializer.validated_data["event_id"]).exists():
            return Response(
                {
                    "message": "the given event already exists"
                },
                status=status.HTTP_409_CONFLICT
            )

        event = serializer.save(
            project_id=project_id,
            data=event_data
        )

        event.save()

        return Response(
            {
                "message": "the event has been received"
            },
            status=status.HTTP_200_OK
        )

    def post(self, request, project_id, format=None):
        self._authenticate(request, project_id)

        serializer = EventSerializer(data=request.data)

        if serializer.is_valid():
            return self._process_event(project_id, serializer, request.data)
        else:
            return Response(
                {
                    "message": "invalid event payload"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
