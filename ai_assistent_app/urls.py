from django.urls import path

from ai_assistent_app.views import (
    AssistantHealthView,
    ChatMessageFavoriteToggleView,
    ChatThreadListCreateView,
    ChatThreadMessagesView,
    FavoriteMessagesListView,
)

app_name = "ai_assistent_app"

urlpatterns = [
    path("health/", AssistantHealthView.as_view(), name="health"),
    path("threads/", ChatThreadListCreateView.as_view(), name="thread-list-create"),
    path(
        "threads/<int:thread_id>/messages/",
        ChatThreadMessagesView.as_view(),
        name="thread-messages",
    ),
    path(
        "messages/<int:message_id>/favorite/",
        ChatMessageFavoriteToggleView.as_view(),
        name="message-favorite-toggle",
    ),
    path("favorites/", FavoriteMessagesListView.as_view(), name="favorite-messages-list"),
]
