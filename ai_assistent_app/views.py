from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_assistent_app.models import ChatMessage, ChatThread
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
                "results": [
                    {
                        "id": thread.id,
                        "title": thread.title,
                        "created_at": thread.created_at,
                        "updated_at": thread.updated_at,
                    }
                    for thread in threads
                ],
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        title = request.data.get("title", "")
        if title is None:
            title = ""
        if not isinstance(title, str):
            return Response({"error": "Поле title должно быть строкой."}, status=status.HTTP_400_BAD_REQUEST)

        thread = ChatThread.objects.create(user=request.user, title=title.strip())
        return Response(
            {
                "id": thread.id,
                "title": thread.title,
                "created_at": thread.created_at,
                "updated_at": thread.updated_at,
            },
            status=status.HTTP_201_CREATED,
        )


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

    def get(self, request, thread_id):
        thread, error_response = self._get_thread(request, thread_id)
        if error_response is not None:
            return error_response

        messages = ChatMessage.objects.filter(thread=thread).order_by("created_at", "id")
        return Response(
            {"results": [self._serialize_message(message) for message in messages]},
            status=status.HTTP_200_OK,
        )

    def post(self, request, thread_id):
        thread, error_response = self._get_thread(request, thread_id)
        if error_response is not None:
            return error_response

        content = request.data.get("content")
        if not isinstance(content, str) or not content.strip():
            return Response(
                {"error": "Поле content обязательно и должно быть непустой строкой."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        assistant_content = request.data.get("assistant_content")
        create_assistant_message = isinstance(assistant_content, str) and assistant_content.strip()

        with transaction.atomic():
            user_message = ChatMessage.objects.create(
                thread=thread,
                role=ChatMessage.Role.USER,
                content=content.strip(),
            )

            assistant_message = None
            if create_assistant_message:
                assistant_message = ChatMessage.objects.create(
                    thread=thread,
                    role=ChatMessage.Role.ASSISTANT,
                    content=assistant_content.strip(),
                )

        results = [self._serialize_message(user_message)]
        if assistant_message is not None:
            results.append(self._serialize_message(assistant_message))

        return Response({"results": results}, status=status.HTTP_201_CREATED)


class ChatMessageFavoriteToggleView(APIView):
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

    def patch(self, request, message_id):
        message = ChatMessage.objects.filter(id=message_id).select_related("thread").first()
        if message is None:
            return Response({"error": "Сообщение не найдено."}, status=status.HTTP_404_NOT_FOUND)

        if message.thread.user_id != request.user.id:
            return Response({"error": "Доступ запрещен."}, status=status.HTTP_403_FORBIDDEN)

        is_favorite = request.data.get("is_favorite")
        if is_favorite is None:
            message.is_favorite = not message.is_favorite
        elif isinstance(is_favorite, bool):
            message.is_favorite = is_favorite
        else:
            return Response(
                {"error": "Поле is_favorite должно быть булевым значением."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        message.save(update_fields=["is_favorite"])
        return Response(self._serialize_message(message), status=status.HTTP_200_OK)


class FavoriteMessagesListView(APIView):
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

    def get(self, request):
        messages = ChatMessage.objects.filter(
            thread__user=request.user,
            is_favorite=True,
        ).order_by("-created_at", "-id")

        return Response(
            {"results": [self._serialize_message(message) for message in messages]},
            status=status.HTTP_200_OK,
        )
