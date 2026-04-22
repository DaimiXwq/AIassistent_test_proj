from django.contrib import admin

from ai_assistent_app.models import ChatMessage, ChatThread


@admin.register(ChatThread)
class ChatThreadAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("title", "user__username", "user__email")


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "thread", "role", "is_favorite", "created_at")
    list_filter = ("is_favorite", "role", "created_at")
    search_fields = ("content", "thread__title", "thread__user__username", "thread__user__email")
