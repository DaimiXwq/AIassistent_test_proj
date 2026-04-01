from rest_framework import serializers


class ParseResultSerializer(serializers.Serializer):
    text = serializers.CharField()
    chunks = serializers.ListField(child=serializers.CharField())
    metadata = serializers.DictField(required=False)


class SaveDocumentRequestSerializer(ParseResultSerializer):
    pass


class SaveDocumentResponseSerializer(serializers.Serializer):
    document_id = serializers.IntegerField()
    chunks_count = serializers.IntegerField()
    status = serializers.CharField()


class SearchRequestSerializer(serializers.Serializer):
    query = serializers.CharField()
    top_k = serializers.IntegerField(required=False, min_value=1, default=5)


class SearchResultItemSerializer(serializers.Serializer):
    text = serializers.CharField()
    score = serializers.FloatField()
    document_id = serializers.IntegerField()


class SearchResponseSerializer(serializers.Serializer):
    results = SearchResultItemSerializer(many=True)


class ErrorEnvelopeSerializer(serializers.Serializer):
    code = serializers.CharField()
    message = serializers.CharField()
    details = serializers.JSONField(required=False)
