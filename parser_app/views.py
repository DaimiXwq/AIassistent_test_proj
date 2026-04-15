import logging
import os
import tempfile

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.chunker import SmatChunker
from db_server.services import DocumentService
from parser_app.parsers.factory import ParserFactory
from parser_app.serializer import ParserFileSerializer
from users.authentication import DEFAULT_API_AUTHENTICATION_CLASSES
from users.drf_permissions import IsActiveUser

logger = logging.getLogger(__name__)


class ParseDocumentView(APIView):
    authentication_classes = DEFAULT_API_AUTHENTICATION_CLASSES
    permission_classes = [IsAuthenticated, IsActiveUser]

    def post(self, request):
        serializer = ParserFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data["file"]
        tmp_path = None

        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp_path = tmp.name
                for chunk in file.chunks():
                    tmp.write(chunk)

            ext = file.name.split(".")[-1].lower()
            parser = ParserFactory.get_parser(ext)
            parsed_data = parser.parse(tmp_path)

            chunks = SmatChunker().split_text(parsed_data["text"])
            document = DocumentService.save_document(
                {
                    "chunks": chunks,
                    "title": file.name,
                    "source": "parser_api",
                    "knowledge_base_id": request.data.get("knowledge_base_id"),
                    "created_by": request.user,
                    "actor_user": request.user,
                }
            )

            return Response(
                {
                    "document_id": document.id,
                    "chunks_count": len(chunks),
                    "knowledge_base_id": document.knowledge_base_id,
                    "visibility": document.knowledge_base.visibility,
                    "owner_id": document.knowledge_base.owner_id,
                },
                status=status.HTTP_200_OK,
            )
        except Exception:
            logger.exception("Unexpected parser pipeline failure")
            return Response(
                {"error": "Unexpected server error while processing document."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    logger.exception("Failed to remove temporary file: %s", tmp_path)
