from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser


class StoreEvent(APIView):
    parser_classes = [JSONParser]

    def post(self, request, project_id, format=None):
        return Response(
            {
                "result": "ok"
            },
            status=status.HTTP_200_OK
        )
