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

    def _process_event(self, project_id, serializer, event_data):
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return Response(
                {
                    "message": "the requested project doesn't exist"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if Event.objects.filter(
                id=serializer.validated_data["event_id"]).exists():
            return Response(
                {
                    "message": "the given event already exists"
                },
                status=status.HTTP_409_CONFLICT
            )

        event = serializer.save(
            project=project,
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
