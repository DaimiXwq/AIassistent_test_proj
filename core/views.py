from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.chunker import SmatChunker


class ChunkTextSerializer(serializers.Serializer):
    text = serializers.CharField()
    metadata = serializers.JSONField(required=False)


class ChunkTextView(APIView):
    def post(self, request):
        serializer = ChunkTextSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        chunker = SmatChunker()
        chunks = chunker.split_text(serializer.validated_data["text"])

        return Response(
            {
                "chunks": chunks,
                "metadata": serializer.validated_data.get("metadata", {}),
            },
            status=status.HTTP_200_OK,
        )
