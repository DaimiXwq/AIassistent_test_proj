import numpy as np
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from db_server.models import Embedding
from db_server.services import DocumentService


def cosine_similarity(a, b):
    va = np.array(a)
    vb = np.array(b)
    return float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb)))


class SaveDocumentSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, default="Uploaded Document")
    source = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    chunks = serializers.ListField(child=serializers.CharField())


class VectorSearchSerializer(serializers.Serializer):
    query_vector = serializers.ListField(child=serializers.FloatField())
    top_k = serializers.IntegerField(required=False, min_value=1, default=5)


class SaveDocumentAPIView(APIView):
    def post(self, request):
        serializer = SaveDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = {
            "chunks": serializer.validated_data["chunks"],
        }
        document = DocumentService.save_document(data)

        if serializer.validated_data.get("title"):
            document.title = serializer.validated_data["title"]
        if "source" in serializer.validated_data:
            document.source = serializer.validated_data["source"]
        document.save(update_fields=["title", "source"])

        return Response(
            {
                "document_id": document.id,
                "chunks_count": len(serializer.validated_data["chunks"]),
            },
            status=status.HTTP_201_CREATED,
        )


class VectorSearchAPIView(APIView):
    def post(self, request):
        serializer = VectorSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        query_vector = serializer.validated_data["query_vector"]
        top_k = serializer.validated_data["top_k"]

        results = []
        embeddings = Embedding.objects.select_related("chunk", "chunk__document").all()

        for emb in embeddings:
            results.append(
                {
                    "text": emb.chunk.text,
                    "score": cosine_similarity(query_vector, emb.vector),
                    "document_id": emb.chunk.document.id,
                }
            )

        results.sort(key=lambda x: x["score"], reverse=True)

        return Response({"results": results[:top_k]}, status=status.HTTP_200_OK)
