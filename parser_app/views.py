# from django.shortcuts import render
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import ParserFileSerializer
from core.dispatcher import SourceDispatcher
from core.serializers import ParseResultSerializer
from core.errors import build_error_response
import tempfile

class ParseDocumentView(APIView):

    def post(self, request):
        serializer = ParserFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data["file"]

        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                for chunk in file.chunks():
                    tmp.write(chunk)

            result = SourceDispatcher.process_file(tmp.name)
            response_serializer = ParseResultSerializer(data=result)
            response_serializer.is_valid(raise_exception=True)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return build_error_response(
                code="parse_failed",
                message="Could not parse uploaded file",
                details={"error": str(e)},
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
