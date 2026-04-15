import json
import logging
import os
import tempfile
from urllib import error, request as urlrequest

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from parser_app.parsers.factory import ParserFactory
from parser_app.serializer import ParserFileSerializer

logger = logging.getLogger(__name__)


class ParseDocumentView(APIView):
    @staticmethod
    def _post_json(path, payload):
        body = json.dumps(payload).encode("utf-8")
        endpoint = f"{settings.INTERNAL_API_BASE_URL.rstrip('/')}{path}"
        req = urlrequest.Request(
            endpoint,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlrequest.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))

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

            chunk_result = self._post_json(
                "/api/core/chunk/",
                {
                    "text": parsed_data["text"],
                    "metadata": parsed_data.get("metadata", {}),
                },
            )

            document_result = self._post_json(
                "/api/db/documents/pipeline-result/",
                {
                    "chunks": chunk_result["chunks"],
                    "title": file.name,
                    "source": "parser_api",
                },
            )

            return Response(document_result, status=status.HTTP_200_OK)
        except error.HTTPError as e:
            return Response(
                {"error": f"Internal API error: {e.reason}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except error.URLError as e:
            return Response(
                {"error": f"Internal API unavailable: {e.reason}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as e:
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
