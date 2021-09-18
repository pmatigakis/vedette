from celery import chain

from rest_framework.exceptions import NotAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer

from events.negotiation import IgnoreClientContentNegotiation
from events.parsers import GzippedJSONParser

from .serializers import RawEventSerializer
from .tasks import capture_event, process_event


class StoreEvent(APIView):
    parser_classes = [GzippedJSONParser]
    renderer_classes = [JSONRenderer]
    content_negotiation_class = IgnoreClientContentNegotiation

    def _extract_public_key(self, request):
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
                        public_key = auth_values[1].strip()
                    except ValueError:
                        raise NotAuthenticated(detail="invalid authentication")
                    break

        if not public_key:
            raise NotAuthenticated(detail="missing public key")

        return public_key

    def post(self, request, project_id, format=None):
        public_key = self._extract_public_key(request)

        serializer = RawEventSerializer(data=request.data)

        if serializer.is_valid():
            event_processing_clain = chain(
                capture_event.s(project_id, public_key, request.data),
                process_event.s()
            )
            event_processing_clain.delay()

            return Response(
                {
                    "message": "the event has been received"
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    "message": "invalid event payload"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
