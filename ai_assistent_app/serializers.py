from rest_framework import serializers

from core.serializers import SemanticMatchSerializer
from db_server.serializers import DocumentResponseSerializer


class OrchestrateRequestSerializer(serializers.Serializer):
    query = serializers.CharField()
    top_k = serializers.IntegerField(min_value=1, max_value=50, required=False, default=5)
    document_id = serializers.IntegerField(min_value=1, required=False)


class OrchestrateResponseSerializer(serializers.Serializer):
    query = serializers.CharField()
    top_k = serializers.IntegerField()
    matches = SemanticMatchSerializer(many=True)
    document = DocumentResponseSerializer(required=False, allow_null=True)
