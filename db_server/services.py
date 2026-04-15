from rest_framework.exceptions import PermissionDenied

from .models import Chunk, Document, Embedding, KnowledgeBase, KnowledgeBaseMember
from core.embeddings import EmbeddingService


class KnowledgeBaseAccessService:
    MANAGE_ROLES = {KnowledgeBaseMember.Role.OWNER, KnowledgeBaseMember.Role.EDITOR}
    READ_ROLES = {
        KnowledgeBaseMember.Role.OWNER,
        KnowledgeBaseMember.Role.EDITOR,
        KnowledgeBaseMember.Role.VIEWER,
    }

    @staticmethod
    def _get_user_membership(knowledge_base, user):
        if user is None or not getattr(user, "is_authenticated", False):
            return None
        return KnowledgeBaseMember.objects.filter(
            knowledge_base=knowledge_base,
            user=user,
        ).first()

    @staticmethod
    def can_manage_documents(knowledge_base, user):
        if (
            user is not None
            and getattr(user, "is_authenticated", False)
            and knowledge_base.owner_id == user.id
        ):
            return True

        membership = KnowledgeBaseAccessService._get_user_membership(knowledge_base, user)
        if membership and membership.role in KnowledgeBaseAccessService.MANAGE_ROLES:
            return True

        # System fallback for legacy shared default KB usage without explicit memberships.
        if (
            user is None
            and knowledge_base.owner_id is None
            and not knowledge_base.members.exists()
            and knowledge_base.visibility == KnowledgeBase.Visibility.SHARED
        ):
            return True

        return False

    @staticmethod
    def assert_can_manage_documents(knowledge_base, user):
        if not KnowledgeBaseAccessService.can_manage_documents(knowledge_base, user):
            raise PermissionDenied("Only knowledge base owner/editor can manage documents.")

    @staticmethod
    def can_read_documents(knowledge_base, user):
        if knowledge_base.visibility == KnowledgeBase.Visibility.SHARED:
            return True

        if (
            user is not None
            and getattr(user, "is_authenticated", False)
            and knowledge_base.owner_id == user.id
        ):
            return True

        membership = KnowledgeBaseAccessService._get_user_membership(knowledge_base, user)
        return bool(membership and membership.role in KnowledgeBaseAccessService.READ_ROLES)


class DocumentService:
    @staticmethod
    def _resolve_knowledge_base(data):
        knowledge_base_id = data.get("knowledge_base_id")
        if knowledge_base_id:
            return KnowledgeBase.objects.get(id=knowledge_base_id)

        default_kb, _ = KnowledgeBase.objects.get_or_create(
            slug="default",
            defaults={
                "name": "Default",
                "visibility": KnowledgeBase.Visibility.SHARED,
                "description": "Default shared knowledge base",
                "owner": None,
            },
        )
        return default_kb

    @staticmethod
    def save_document(data):
        knowledge_base = DocumentService._resolve_knowledge_base(data)
        KnowledgeBaseAccessService.assert_can_manage_documents(
            knowledge_base=knowledge_base,
            user=data.get("actor_user"),
        )
        document = Document.objects.create(
            title=data.get("title") or "Uploaded Document",
            source=data.get("source") or "api",
            knowledge_base=knowledge_base,
            created_by=data.get("created_by"),
        )

        embedding_service = EmbeddingService()

        for i, chunk_text in enumerate(data["chunks"]):
            chunk = Chunk.objects.create(
                document=document,
                text=chunk_text,
                index=i,
            )

            vector = embedding_service.generate(chunk_text)

            Embedding.objects.create(
                chunk=chunk,
                vector=vector,
            )

        return document

    @staticmethod
    def soft_delete_document(document, actor_user):
        KnowledgeBaseAccessService.assert_can_manage_documents(
            knowledge_base=document.knowledge_base,
            user=actor_user,
        )
        document.soft_delete()
