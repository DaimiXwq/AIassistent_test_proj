from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ai_assistent_app.models import ChatMessage, ChatThread


class ChatThreadMessagesViewTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="assistant-user", password="StrongPass123!")
        self.client.force_authenticate(user=self.user)
        self.thread = ChatThread.objects.create(user=self.user, title="Thread")

    def test_post_accepts_legacy_payload_without_role(self):
        response = self.client.post(
            reverse("ai_assistent_app:thread-messages", kwargs={"thread_id": self.thread.id}),
            {"content": "Hello"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["role"], ChatMessage.Role.USER)
        self.assertEqual(ChatMessage.objects.filter(thread=self.thread).count(), 1)

    def test_post_creates_assistant_message_when_assistant_content_is_provided(self):
        response = self.client.post(
            reverse("ai_assistent_app:thread-messages", kwargs={"thread_id": self.thread.id}),
            {"content": "User question", "assistant_content": "Assistant response"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["role"], ChatMessage.Role.USER)
        self.assertEqual(response.data["results"][1]["role"], ChatMessage.Role.ASSISTANT)
        self.assertEqual(ChatMessage.objects.filter(thread=self.thread).count(), 2)


class ChatMessageFavoriteToggleViewTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="favorite-user",
            password="StrongPass123!",
        )
        self.client.force_authenticate(user=self.user)
        self.thread = ChatThread.objects.create(user=self.user, title="Favorites")
        self.message = ChatMessage.objects.create(
            thread=self.thread,
            role=ChatMessage.Role.USER,
            content="Message",
            is_favorite=False,
        )

    def test_patch_without_is_favorite_toggles_value(self):
        response = self.client.patch(
            reverse("ai_assistent_app:message-favorite-toggle", kwargs={"message_id": self.message.id}),
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.message.refresh_from_db()
        self.assertTrue(self.message.is_favorite)
