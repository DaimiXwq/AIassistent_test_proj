# from django.shortcuts import render
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import ParserFileSerializer
from core.dispatcher import SourceDispatcher
from db_server.services import DocumentService
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

            document = DocumentService.save_document(result)

            return Response({
                "document_id": document.id,
                "chunks_count": len(result["chunks"])
                }, 
                status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
