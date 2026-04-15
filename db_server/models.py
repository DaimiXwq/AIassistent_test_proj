from django.db import models


class KnowledgeBase(models.Model):
    class Visibility(models.TextChoices):
        SHARED = "shared", "Shared"
        PERSONAL = "personal", "Personal"

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    visibility = models.CharField(max_length=20, choices=Visibility.choices)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Document(models.Model):
    title = models.CharField(max_length=255)
    source = models.CharField(max_length=255, null=True)
    knowledge_base = models.ForeignKey(
        KnowledgeBase,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["knowledge_base", "created_at"], name="db_server_d_knowled_324a38_idx"),
        ]


class Chunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="chunks")
    text = models.TextField()
    index = models.IntegerField()
    metadata = models.JSONField(default=dict)


class Embedding(models.Model):
    chunk = models.OneToOneField(Chunk, on_delete=models.CASCADE)
    vector = models.JSONField()  # заменим на pgvector
    created_at = models.DateTimeField(auto_now_add=True)
