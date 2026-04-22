from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_assistent_app.models import ChatMessage, ChatThread
from ai_assistent_app.serializers import (
    ChatMessageCreateSerializer,
    ChatMessageFavoriteSerializer,
    ChatMessageSerializer,
    ChatThreadCreateSerializer,
    ChatThreadSerializer,
)
from users.authentication import DEFAULT_API_AUTHENTICATION_CLASSES
from users.drf_permissions import IsActiveUser


class AssistantHealthView(APIView):
    def get(self, request):
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class ChatThreadListCreateView(APIView):
    authentication_classes = DEFAULT_API_AUTHENTICATION_CLASSES
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        try:
            page = int(request.query_params.get("page", 1))
            page_size = int(request.query_params.get("page_size", 20))
        except (TypeError, ValueError):
            return Response(
                {"error": "Параметры page и page_size должны быть целыми числами."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if page < 1 or page_size < 1:
            return Response(
                {"error": "Параметры page и page_size должны быть больше 0."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = ChatThread.objects.filter(user=request.user).order_by("-updated_at", "-id")
        total = queryset.count()

        start = (page - 1) * page_size
        end = start + page_size
        threads = queryset[start:end]

        return Response(
            {
                "page": page,
                "page_size": page_size,
                "total": total,
                "results": ChatThreadSerializer(threads, many=True).data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = ChatThreadCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        title = serializer.validated_data.get("title", "").strip()
        thread = ChatThread.objects.create(user=request.user, title=title)
        return Response(ChatThreadSerializer(thread).data, status=status.HTTP_201_CREATED)


class ChatThreadMessagesView(APIView):
    authentication_classes = DEFAULT_API_AUTHENTICATION_CLASSES
    permission_classes = [IsAuthenticated, IsActiveUser]

    def _get_thread(self, request, thread_id):
        thread = ChatThread.objects.filter(id=thread_id).select_related("user").first()
        if thread is None:
            return None, Response({"error": "Тред не найден."}, status=status.HTTP_404_NOT_FOUND)
        if thread.user_id != request.user.id:
            return None, Response({"error": "Доступ запрещен."}, status=status.HTTP_403_FORBIDDEN)
        return thread, None

    def get(self, request, thread_id):
        thread, error_response = self._get_thread(request, thread_id)
        if error_response is not None:
            return error_response

        messages = ChatMessage.objects.filter(thread=thread).order_by("created_at", "id")
        return Response(
            {"results": ChatMessageSerializer(messages, many=True).data},
            status=status.HTTP_200_OK,
        )

    def post(self, request, thread_id):
        thread, error_response = self._get_thread(request, thread_id)
        if error_response is not None:
            return error_response

        serializer = ChatMessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            created_messages = [
                ChatMessage.objects.create(
                    thread=thread,
                    role=serializer.validated_data["role"],
                    content=serializer.validated_data["content"],
                )
            ]

            assistant_content = serializer.validated_data.get("assistant_content")
            if assistant_content:
                created_messages.append(
                    ChatMessage.objects.create(
                        thread=thread,
                        role=ChatMessage.Role.ASSISTANT,
                        content=assistant_content,
                    )
                )

        return Response(
            {"results": ChatMessageSerializer(created_messages, many=True).data},
            status=status.HTTP_201_CREATED,
        )


class ChatMessageFavoriteToggleView(APIView):
    authentication_classes = DEFAULT_API_AUTHENTICATION_CLASSES
    permission_classes = [IsAuthenticated, IsActiveUser]

    def patch(self, request, message_id):
        message = ChatMessage.objects.filter(id=message_id).select_related("thread").first()
        if message is None:
            return Response({"error": "Сообщение не найдено."}, status=status.HTTP_404_NOT_FOUND)

        if message.thread.user_id != request.user.id:
            return Response({"error": "Доступ запрещен."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ChatMessageFavoriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message.is_favorite = serializer.validated_data.get("is_favorite", not message.is_favorite)
        message.save(update_fields=["is_favorite"])
        return Response(ChatMessageSerializer(message).data, status=status.HTTP_200_OK)


class FavoriteMessagesListView(APIView):
    authentication_classes = DEFAULT_API_AUTHENTICATION_CLASSES
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        messages = ChatMessage.objects.filter(
            thread__user=request.user,
            is_favorite=True,
        ).order_by("-created_at", "-id")

        return Response(
            {"results": ChatMessageSerializer(messages, many=True).data},
            status=status.HTTP_200_OK,
        )
