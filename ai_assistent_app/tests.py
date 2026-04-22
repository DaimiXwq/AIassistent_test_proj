from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from ai_assistent_app.models import ChatMessage, ChatThread
from ai_assistent_app.views import ChatThreadListCreateView


class AssistantApiTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="alice", password="pass1234")
        self.other_user = user_model.objects.create_user(username="bob", password="pass1234")
        self.inactive_user = user_model.objects.create_user(
            username="inactive",
            password="pass1234",
            is_active=False,
        )

        self.my_thread = ChatThread.objects.create(user=self.user, title="My thread")
        self.other_thread = ChatThread.objects.create(user=self.other_user, title="Other thread")

        self.my_message = ChatMessage.objects.create(
            thread=self.my_thread,
            role=ChatMessage.Role.USER,
            content="my message",
        )
        self.other_message = ChatMessage.objects.create(
            thread=self.other_thread,
            role=ChatMessage.Role.USER,
            content="other message",
        )

    def test_active_authenticated_user_can_create_thread(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("ai_assistent_app:thread-list-create"),
            {"title": "New thread"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            ChatThread.objects.filter(user=self.user, title="New thread").exists(),
        )

    def test_user_gets_only_own_threads(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("ai_assistent_app:thread-list-create"))

        self.assertEqual(response.status_code, 200)
        thread_ids = [item["id"] for item in response.json()["results"]]
        self.assertEqual(thread_ids, [self.my_thread.id])

    def test_user_gets_only_own_messages(self):
        self.client.force_login(self.user)

        own_response = self.client.get(
            reverse("ai_assistent_app:thread-messages", args=[self.my_thread.id]),
        )
        foreign_response = self.client.get(
            reverse("ai_assistent_app:thread-messages", args=[self.other_thread.id]),
        )

        self.assertEqual(own_response.status_code, 200)
        self.assertEqual(own_response.json()["results"][0]["id"], self.my_message.id)
        self.assertEqual(foreign_response.status_code, 403)

    def test_user_can_add_message_only_to_own_thread(self):
        self.client.force_login(self.user)

        own_response = self.client.post(
            reverse("ai_assistent_app:thread-messages", args=[self.my_thread.id]),
            {"role": ChatMessage.Role.USER, "content": "hello"},
            content_type="application/json",
        )
        foreign_response = self.client.post(
            reverse("ai_assistent_app:thread-messages", args=[self.other_thread.id]),
            {"role": ChatMessage.Role.USER, "content": "hack"},
            content_type="application/json",
        )

        self.assertEqual(own_response.status_code, 201)
        self.assertEqual(foreign_response.status_code, 403)
        self.assertTrue(ChatMessage.objects.filter(thread=self.my_thread, content="hello").exists())
        self.assertFalse(ChatMessage.objects.filter(thread=self.other_thread, content="hack").exists())

    def test_user_can_set_and_unset_favorite_for_own_message(self):
        self.client.force_login(self.user)

        set_response = self.client.patch(
            reverse("ai_assistent_app:message-favorite-toggle", args=[self.my_message.id]),
            {"is_favorite": True},
            content_type="application/json",
        )
        self.my_message.refresh_from_db()

        unset_response = self.client.patch(
            reverse("ai_assistent_app:message-favorite-toggle", args=[self.my_message.id]),
            {"is_favorite": False},
            content_type="application/json",
        )
        self.my_message.refresh_from_db()

        self.assertEqual(set_response.status_code, 200)
        self.assertEqual(unset_response.status_code, 200)
        self.assertFalse(self.my_message.is_favorite)

    def test_user_cannot_toggle_favorite_for_foreign_message(self):
        self.client.force_login(self.user)

        response = self.client.patch(
            reverse("ai_assistent_app:message-favorite-toggle", args=[self.other_message.id]),
            {"is_favorite": True},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    def test_favorites_returns_only_own_messages_and_is_sorted_desc(self):
        self.client.force_login(self.user)

        old_message = ChatMessage.objects.create(
            thread=self.my_thread,
            role=ChatMessage.Role.USER,
            content="old favorite",
            is_favorite=True,
        )
        new_message = ChatMessage.objects.create(
            thread=self.my_thread,
            role=ChatMessage.Role.ASSISTANT,
            content="new favorite",
            is_favorite=True,
        )

        ChatMessage.objects.filter(id=old_message.id).update(
            created_at=timezone.now() - timezone.timedelta(days=1),
        )
        old_message.refresh_from_db()
        new_message.refresh_from_db()

        ChatMessage.objects.filter(id=self.other_message.id).update(is_favorite=True)

        response = self.client.get(reverse("ai_assistent_app:favorite-messages-list"))

        self.assertEqual(response.status_code, 200)
        favorite_ids = [item["id"] for item in response.json()["results"]]
        self.assertEqual(favorite_ids, [new_message.id, old_message.id])
        self.assertNotIn(self.other_message.id, favorite_ids)

    def test_inactive_user_gets_403_from_is_active_user(self):
        request = APIRequestFactory().get(reverse("ai_assistent_app:thread-list-create"))
        force_authenticate(request, user=self.inactive_user)

        response = ChatThreadListCreateView.as_view()(request)

        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_access_returns_401(self):
        response_threads = self.client.get(reverse("ai_assistent_app:thread-list-create"))
        response_messages = self.client.get(
            reverse("ai_assistent_app:thread-messages", args=[self.my_thread.id]),
        )

        self.assertEqual(response_threads.status_code, 401)
        self.assertEqual(response_messages.status_code, 401)
