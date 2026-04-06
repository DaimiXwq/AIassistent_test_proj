# from django.shortcuts import render
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import ParserFileSerializer
from core.dispatcher import SourceDispatcher
from db_server.services import DocumentService
import tempfile
import os

class ParseDocumentView(APIView):

    def post(self, request):
        serializer = ParserFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data["file"]

        tmp_path = None

        try:
            _, file_ext = os.path.splitext(file.name or "")

            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
                for chunk in file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            result = SourceDispatcher.process_file(tmp_path)

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
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
