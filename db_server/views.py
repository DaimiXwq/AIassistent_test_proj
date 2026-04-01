from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.errors import build_error_response
from core.serializers import SaveDocumentRequestSerializer, SaveDocumentResponseSerializer
from .services import DocumentService


class SaveDocumentView(APIView):

    def post(self, request):
        serializer = SaveDocumentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            document = DocumentService.save_document(serializer.validated_data)
            response_payload = {
                "document_id": document.id,
                "chunks_count": len(serializer.validated_data["chunks"]),
                "status": "saved",
            }
            response_serializer = SaveDocumentResponseSerializer(data=response_payload)
            response_serializer.is_valid(raise_exception=True)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            return build_error_response(
                code="save_failed",
                message="Could not save parsed document",
                details={"error": str(exc)},
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
