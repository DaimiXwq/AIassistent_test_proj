from rest_framework import serializers


class ChunkWithEmbeddingInputSerializer(serializers.Serializer):
    text = serializers.CharField()
    index = serializers.IntegerField()
    metadata = serializers.JSONField(required=False, default=dict)
    embedding = serializers.ListField(
        child=serializers.FloatField(),
        required=False,
        allow_empty=False,
    )


class SaveDocumentRequestSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, default="Uploaded Document")
    source = serializers.CharField(required=False, allow_blank=True, default="api")
    chunks = ChunkWithEmbeddingInputSerializer(many=True)


class EmbeddingSerializer(serializers.Serializer):
    vector = serializers.ListField(child=serializers.FloatField())
    created_at = serializers.DateTimeField()


class ChunkResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    index = serializers.IntegerField()
    text = serializers.CharField()
    metadata = serializers.JSONField()
    embedding = EmbeddingSerializer(allow_null=True)


class DocumentResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    source = serializers.CharField(allow_null=True)
    created_at = serializers.DateTimeField()
    chunks = ChunkResponseSerializer(many=True)


class SaveDocumentResponseSerializer(serializers.Serializer):
    document = DocumentResponseSerializer()


class BatchEmbeddingsRequestSerializer(serializers.Serializer):
    chunk_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
    )


class BatchEmbeddingsItemSerializer(serializers.Serializer):
    chunk_id = serializers.IntegerField()
    vector = serializers.ListField(child=serializers.FloatField())


class BatchEmbeddingsResponseSerializer(serializers.Serializer):
    embeddings = BatchEmbeddingsItemSerializer(many=True)
