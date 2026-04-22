from django.conf import settings
from django.db import models


class ChatThread(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_threads",
    )
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-id"]
        indexes = [
            models.Index(fields=["user", "updated_at"]),
        ]

    def __str__(self):
        return f"ChatThread(id={self.id}, user_id={self.user_id}, title={self.title!r})"


class ChatMessage(models.Model):
    class Role(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"
        SYSTEM = "system", "System"

    id = models.BigAutoField(primary_key=True)
    thread = models.ForeignKey(
        ChatThread,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(max_length=20, choices=Role.choices)
    content = models.TextField()
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["created_at", "id"]
        indexes = [
            models.Index(fields=["thread", "created_at"]),
            models.Index(fields=["thread", "is_favorite", "created_at"]),
        ]

    def __str__(self):
        return (
            f"ChatMessage(id={self.id}, thread_id={self.thread_id}, "
            f"role={self.role}, favorite={self.is_favorite})"
        )
