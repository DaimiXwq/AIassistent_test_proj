from rest_framework import serializers

from ai_assistent_app.constants import MAX_MESSAGE_LENGTH, MAX_THREAD_TITLE_LENGTH
from ai_assistent_app.models import ChatMessage, ChatThread


class ChatThreadCreateSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, allow_blank=True, max_length=MAX_THREAD_TITLE_LENGTH)


class ChatMessageCreateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=[ChatMessage.Role.USER, ChatMessage.Role.ASSISTANT])
    content = serializers.CharField(allow_blank=False, trim_whitespace=True, max_length=MAX_MESSAGE_LENGTH)


class ChatMessageFavoriteSerializer(serializers.Serializer):
    is_favorite = serializers.BooleanField()


class ChatThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatThread
        fields = ("id", "title", "created_at", "updated_at")


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ("id", "thread_id", "role", "content", "is_favorite", "created_at")
