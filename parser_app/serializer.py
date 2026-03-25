from rest_framework import serializers
class ParserFileSerializer(serializers.Serializer):
    file = serializers.FileField()