from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_assistent_app.models import ChatMessage, ChatThread
from users.authentication import DEFAULT_API_AUTHENTICATION_CLASSES
from users.drf_permissions import IsActiveUser


class AssistantHealthView(APIView):
    authentication_classes = DEFAULT_API_AUTHENTICATION_CLASSES
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class ChatBaseAPIView(APIView):
    authentication_classes = DEFAULT_API_AUTHENTICATION_CLASSES
    permission_classes = [IsAuthenticated, IsActiveUser]

    @staticmethod
    def _serialize_message(message):
        return {
            "id": message.id,
            "thread_id": message.thread_id,
            "role": message.role,
            "content": message.content,
            "is_favorite": message.is_favorite,
            "created_at": message.created_at,
        }

    def _get_thread_for_user(self, request, thread_id):
        thread = ChatThread.objects.filter(id=thread_id).first()
        if thread is None:
            return None, Response({"error": "Thread not found."}, status=status.HTTP_404_NOT_FOUND)
        if thread.user_id != request.user.id:
            return None, Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        return thread, None

    def _get_message_for_user(self, request, message_id):
        message = ChatMessage.objects.select_related("thread").filter(id=message_id).first()
        if message is None:
            return None, Response({"error": "Message not found."}, status=status.HTTP_404_NOT_FOUND)
        if message.thread.user_id != request.user.id:
            return None, Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        return message, None


class ChatThreadListCreateView(ChatBaseAPIView):
    def get(self, request):
        try:
            page = max(int(request.query_params.get("page", 1)), 1)
            page_size = min(max(int(request.query_params.get("page_size", 20)), 1), 100)
        except ValueError:
            return Response({"error": "page and page_size must be integers."}, status=status.HTTP_400_BAD_REQUEST)

        queryset = ChatThread.objects.filter(user=request.user)
        total = queryset.count()
        offset = (page - 1) * page_size
        threads = queryset[offset : offset + page_size]

        return Response(
            {
                "count": total,
                "page": page,
                "page_size": page_size,
                "results": [
                    {
                        "id": thread.id,
                        "created_at": thread.created_at,
                    }
                    for thread in threads
                ],
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        title = request.data.get("title", "")
        if title is not None and not isinstance(title, str):
            return Response({"error": "title must be a string."}, status=status.HTTP_400_BAD_REQUEST)

        thread = ChatThread.objects.create(user=request.user, title=(title or "").strip())
        return Response(
            {
                "id": thread.id,
                "created_at": thread.created_at,
            },
            status=status.HTTP_201_CREATED,
        )


class ChatThreadMessagesView(ChatBaseAPIView):
    def get(self, request, thread_id):
        thread, error_response = self._get_thread_for_user(request, thread_id)
        if error_response is not None:
            return error_response

        messages = thread.messages.order_by("created_at", "id")
        return Response(
            {
                "thread_id": thread.id,
                "results": [self._serialize_message(message) for message in messages],
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, thread_id):
        thread, error_response = self._get_thread_for_user(request, thread_id)
        if error_response is not None:
            return error_response

        content = request.data.get("content")
        if not isinstance(content, str) or not content.strip():
            return Response(
                {"error": "content is required and must be a non-empty string."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        assistant_reply = request.data.get("assistant_reply")
        if assistant_reply is not None and (not isinstance(assistant_reply, str) or not assistant_reply.strip()):
            return Response(
                {"error": "assistant_reply must be a non-empty string when provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            user_message = ChatMessage.objects.create(
                thread=thread,
                role=ChatMessage.ROLE_USER,
                content=content.strip(),
            )
            created_messages = [user_message]

            if assistant_reply is not None:
                assistant_message = ChatMessage.objects.create(
                    thread=thread,
                    role=ChatMessage.ROLE_ASSISTANT,
                    content=assistant_reply.strip(),
                )
                created_messages.append(assistant_message)

        return Response(
            {"results": [self._serialize_message(message) for message in created_messages]},
            status=status.HTTP_201_CREATED,
        )


class ChatMessageFavoriteToggleView(ChatBaseAPIView):
    def patch(self, request, message_id):
        message, error_response = self._get_message_for_user(request, message_id)
        if error_response is not None:
            return error_response

        explicit_value = request.data.get("is_favorite")
        if explicit_value is None:
            message.is_favorite = not message.is_favorite
        elif isinstance(explicit_value, bool):
            message.is_favorite = explicit_value
        else:
            return Response({"error": "is_favorite must be a boolean."}, status=status.HTTP_400_BAD_REQUEST)

        message.save(update_fields=["is_favorite"])
        return Response(self._serialize_message(message), status=status.HTTP_200_OK)


class FavoriteMessagesListView(ChatBaseAPIView):
    def get(self, request):
        favorites = ChatMessage.objects.filter(thread__user=request.user, is_favorite=True).order_by("created_at", "id")
        return Response(
            {
                "results": [self._serialize_message(message) for message in favorites],
            },
            status=status.HTTP_200_OK,
        )
