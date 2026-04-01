from rest_framework import serializers


class SemanticSearchRequestSerializer(serializers.Serializer):
    query = serializers.CharField()
    top_k = serializers.IntegerField(min_value=1, max_value=50, required=False, default=5)


class SemanticMatchSerializer(serializers.Serializer):
    text = serializers.CharField()
    score = serializers.FloatField()
    document_id = serializers.IntegerField()


class SemanticSearchResponseSerializer(serializers.Serializer):
    query = serializers.CharField()
    top_k = serializers.IntegerField()
    matches = SemanticMatchSerializer(many=True)
