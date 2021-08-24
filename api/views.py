from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser

from events.models import Event
from projects.models import Project

from .serializers import EventSerializer


class GzippedJSONParser(JSONParser):
    def parse(self, stream, media_type=None, parser_context=None):
        # compressed = base64_encode(zlib.compress(payload))

        try:
            return super(GzippedJSONParser, self).parse(stream=stream, media_type=media_type, parser_context=parser_context)
        except Exception as e:
            print(e)
            raise e



class StoreEvent(APIView):
    parser_classes = [GzippedJSONParser]

    def post(self, request, project_id, format=None):
        serializer = EventSerializer(data=request.data)

        if serializer.is_valid():
            try:
                project = Project.objects.get(pk=project_id)
            except Project.DoesNotExist:
                return Response(
                    {
                        "message": "the requested project doesn't exist"
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            try:
                Event.objects.get(id=serializer.validated_data["event_id"])
            except Event.DoesNotExist:
                pass
            else:
                return Response(
                    {
                        "message": "the given event already exists"
                    },
                    status=status.HTTP_409_CONFLICT
                )

            event = serializer.save(
                project=project,
                data=request.data
            )

            event.save()

            return Response(
                {
                    "result": "ok"
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
