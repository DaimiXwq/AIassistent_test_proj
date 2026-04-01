from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from db_server.models import Document
from db_server.services import DocumentService


class DocumentPipelineResultCreateView(APIView):
    def post(self, request):
        chunks = request.data.get("chunks")

        if not isinstance(chunks, list) or not chunks:
            return Response(
                {"error": "'chunks' must be a non-empty list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload = {
            "chunks": chunks,
            "title": request.data.get("title"),
            "source": request.data.get("source"),
        }
        document = DocumentService.save_document(payload)

        return Response(
            {"document_id": document.id, "chunks_count": len(chunks)},
            status=status.HTTP_201_CREATED,
        )


class DocumentRetrieveView(APIView):
    def get(self, request, document_id):
        document = Document.objects.filter(id=document_id).prefetch_related("chunks").first()

        if document is None:
            return Response(
                {"error": "Document not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "id": document.id,
                "title": document.title,
                "source": document.source,
                "created_at": document.created_at,
                "chunks": [
                    {
                        "id": chunk.id,
                        "index": chunk.index,
                        "text": chunk.text,
                        "metadata": chunk.metadata,
                    }
                    for chunk in document.chunks.order_by("index")
                ],
            },
            status=status.HTTP_200_OK,
        )
