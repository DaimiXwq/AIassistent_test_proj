from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.embeddings import EmbeddingService
from db_server.models import Chunk, Document, Embedding
from db_server.serializers import (
    BatchEmbeddingsRequestSerializer,
    BatchEmbeddingsResponseSerializer,
    DocumentResponseSerializer,
    SaveDocumentRequestSerializer,
    SaveDocumentResponseSerializer,
)


class DocumentViewSet(viewsets.ViewSet):
    """API for storing and reading documents with chunks/embeddings."""

    def _document_payload(self, document: Document) -> dict:
        chunks = document.chunks.select_related("embedding").order_by("index")
        return {
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
                    "embedding": (
                        {
                            "vector": chunk.embedding.vector,
                            "created_at": chunk.embedding.created_at,
                        }
                        if hasattr(chunk, "embedding")
                        else None
                    ),
                }
                for chunk in chunks
            ],
        }

    def create(self, request):
        serializer = SaveDocumentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        embedding_service = EmbeddingService()

        document = Document.objects.create(title=data["title"], source=data["source"])

        for chunk_data in data["chunks"]:
            chunk = Chunk.objects.create(
                document=document,
                text=chunk_data["text"],
                index=chunk_data["index"],
                metadata=chunk_data.get("metadata", {}),
            )
            vector = chunk_data.get("embedding") or embedding_service.generate(chunk.text)
            Embedding.objects.create(chunk=chunk, vector=vector)

        response_payload = {"document": self._document_payload(document)}
        response_serializer = SaveDocumentResponseSerializer(response_payload)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        document = Document.objects.filter(pk=pk).first()
        if not document:
            return Response(
                {"detail": "Document not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        response_serializer = DocumentResponseSerializer(self._document_payload(document))
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="batch-embeddings")
    def batch_embeddings(self, request):
        serializer = BatchEmbeddingsRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        chunk_ids = serializer.validated_data["chunk_ids"]
        embeddings = Embedding.objects.filter(chunk_id__in=chunk_ids).values("chunk_id", "vector")

        payload = {"embeddings": list(embeddings)}
        response_serializer = BatchEmbeddingsResponseSerializer(payload)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
