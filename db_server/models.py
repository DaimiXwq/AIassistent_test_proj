import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class KnowledgeBase(models.Model):
    class Visibility(models.TextChoices):
        SHARED = "shared", "Shared"
        PERSONAL = "personal", "Personal"

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    visibility = models.CharField(max_length=20, choices=Visibility.choices)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="owned_knowledge_bases",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.visibility == self.Visibility.PERSONAL and self.owner_id is None:
            raise ValidationError({"owner": "Personal knowledge base must have an owner."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        db_table = "db_server_knowledgebase"
        verbose_name = "Knowledge base"
        verbose_name_plural = "Knowledge bases"


class Document(models.Model):
    class ActiveDocumentManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(is_deleted=False)

    title = models.CharField(max_length=255)
    source = models.CharField(max_length=255, null=True)
    knowledge_base = models.ForeignKey(
        KnowledgeBase,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_documents",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = ActiveDocumentManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "db_server_document"
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        indexes = [
            models.Index(fields=["created_at"], name="db_server_d_created_9c57de_idx"),
            models.Index(fields=["knowledge_base", "created_at"], name="db_server_d_knowled_324a38_idx"),
            models.Index(
                fields=["knowledge_base", "is_deleted", "created_at"],
                name="dbs_doc_kb_del_cr_idx",
            ),
        ]

    def soft_delete(self):
        if self.is_deleted:
            return
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])


class KnowledgeBaseMember(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        EDITOR = "editor", "Editor"
        VIEWER = "viewer", "Viewer"

    knowledge_base = models.ForeignKey(
        KnowledgeBase,
        on_delete=models.CASCADE,
        related_name="members",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="knowledge_base_memberships",
    )
    role = models.CharField(max_length=20, choices=Role.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "db_server_knowledgebase_member"
        verbose_name = "Knowledge base member"
        verbose_name_plural = "Knowledge base members"
        constraints = [
            models.UniqueConstraint(
                fields=["knowledge_base", "user"],
                name="db_server_kbmember_unique_kb_user",
            )
        ]


class KnowledgeBaseInvite(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REVOKED = "revoked", "Revoked"
        EXPIRED = "expired", "Expired"

    knowledge_base = models.ForeignKey(
        KnowledgeBase,
        on_delete=models.CASCADE,
        related_name="invites",
    )
    email = models.EmailField(blank=True)
    invited_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="knowledge_base_invites",
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not self.email and self.invited_user_id is None:
            raise ValidationError({"email": "Either email or invited_user must be provided."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        db_table = "db_server_knowledgebase_invite"
        verbose_name = "Knowledge base invite"
        verbose_name_plural = "Knowledge base invites"


class Chunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="chunks")
    text = models.TextField()
    index = models.IntegerField()
    metadata = models.JSONField(default=dict)

    class Meta:
        db_table = "db_server_chunk"
        verbose_name = "Chunk"
        verbose_name_plural = "Chunks"
        constraints = [
            models.UniqueConstraint(
                fields=["document", "index"],
                name="db_server_chunk_unique_document_index",
            )
        ]


class Embedding(models.Model):
    chunk = models.OneToOneField(Chunk, on_delete=models.CASCADE)
    vector = models.JSONField()  # заменим на pgvector
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "db_server_embedding"
        verbose_name = "Embedding"
        verbose_name_plural = "Embeddings"
