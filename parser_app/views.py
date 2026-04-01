import os
import tempfile

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from parser_app.clients.core_api import CoreAPIClient
from parser_app.clients.db_api import DBAPIClient
from parser_app.clients.exceptions import normalize_exception
from parser_app.parsers.factory import ParserFactory
from .serializer import ParserFileSerializer


class ParseDocumentView(APIView):
    def post(self, request):
        serializer = ParserFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data["file"]

        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                for chunk in file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            ext = os.path.splitext(file.name)[1][1:]
            parser = ParserFactory.get_parser(ext)
            parse_result = parser.parse(tmp_path)

            core_client = CoreAPIClient()
            chunk_result = core_client.chunk_text(
                parse_result["text"],
                metadata=parse_result.get("metadata", {}),
            )

            db_client = DBAPIClient()
            save_result = db_client.save_document(
                title=file.name,
                source="api",
                chunks=chunk_result["chunks"],
            )

            return Response(
                {
                    "document_id": save_result["document_id"],
                    "chunks_count": save_result["chunks_count"],
                },
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            payload, error_status = normalize_exception(exc)
            return Response(payload, status=error_status)
        finally:
            if "tmp_path" in locals() and os.path.exists(tmp_path):
                os.unlink(tmp_path)
