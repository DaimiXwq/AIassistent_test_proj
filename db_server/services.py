from django.db.models import Q
from rest_framework.exceptions import PermissionDenied

from core.embeddings import EmbeddingService
from users.constants import GROUP_TYPE_ADMIN, GROUP_TYPE_HEAD_OF_DEPARTMENT
from users.permissions import get_actor_group_type

from .models import Chunk, Document, Embedding, KnowledgeBase, KnowledgeBaseMember


class KnowledgeBaseAccessService:
    class Operation:
        READ = "read"
        CREATE = "create"
        DELETE = "delete"
        ASSIGN_RIGHTS = "assign_rights"

    OPERATION_ROLE_MATRIX = {
        Operation.READ: {
            KnowledgeBaseMember.Role.OWNER,
            KnowledgeBaseMember.Role.EDITOR,
            KnowledgeBaseMember.Role.VIEWER,
        },
        Operation.CREATE: {
            KnowledgeBaseMember.Role.OWNER,
            KnowledgeBaseMember.Role.EDITOR,
        },
        Operation.DELETE: {
            KnowledgeBaseMember.Role.OWNER,
            KnowledgeBaseMember.Role.EDITOR,
        },
        Operation.ASSIGN_RIGHTS: {
            KnowledgeBaseMember.Role.OWNER,
        },
    }
    MANAGE_ROLES = OPERATION_ROLE_MATRIX[Operation.CREATE]
    READ_ROLES = OPERATION_ROLE_MATRIX[Operation.READ]

    GLOBAL_RBAC_MATRIX = {
        GROUP_TYPE_ADMIN: {
            Operation.READ,
            Operation.CREATE,
            Operation.DELETE,
            Operation.ASSIGN_RIGHTS,
        },
        GROUP_TYPE_HEAD_OF_DEPARTMENT: {
            Operation.READ,
            Operation.CREATE,
            Operation.DELETE,
        },
    }

    @staticmethod
    def _is_authenticated_user(user):
        return user is not None and getattr(user, "is_authenticated", False)

    @staticmethod
    def _get_user_membership(knowledge_base, user):
        if not KnowledgeBaseAccessService._is_authenticated_user(user):
            return None
        return KnowledgeBaseMember.objects.filter(
            knowledge_base=knowledge_base,
            user=user,
        ).first()

    @staticmethod
    def _get_user_allowed_operations(user):
        return KnowledgeBaseAccessService.GLOBAL_RBAC_MATRIX.get(get_actor_group_type(user), set())

    @staticmethod
    def _has_global_access_for_operation(user, operation):
        return operation in KnowledgeBaseAccessService._get_user_allowed_operations(user)

    @staticmethod
    def _get_operation_roles(operation):
        operation_roles = KnowledgeBaseAccessService.OPERATION_ROLE_MATRIX.get(operation)
        if operation_roles is None:
            raise ValueError(f"Unknown operation: {operation}")
        return operation_roles

    @staticmethod
    def _is_shared_read_allowed(knowledge_base, operation):
        return (
            operation == KnowledgeBaseAccessService.Operation.READ
            and knowledge_base.visibility == KnowledgeBase.Visibility.SHARED
        )

    @staticmethod
    def can_access(knowledge_base, user, operation):
        if not KnowledgeBaseAccessService._is_authenticated_user(user):
            return False

        if KnowledgeBaseAccessService._has_global_access_for_operation(user, operation):
            return True

        if KnowledgeBaseAccessService._is_shared_read_allowed(knowledge_base, operation):
            return True

        if knowledge_base.owner_id == user.id:
            return True

        membership = KnowledgeBaseAccessService._get_user_membership(knowledge_base, user)
        operation_roles = KnowledgeBaseAccessService._get_operation_roles(operation)
        return bool(membership and membership.role in operation_roles)

    @staticmethod
    def assert_can_access(knowledge_base, user, operation, message):
        if not KnowledgeBaseAccessService.can_access(knowledge_base, user, operation):
            raise PermissionDenied(message)

    @staticmethod
    def filter_documents_by_operation(queryset, user, operation):
        if not KnowledgeBaseAccessService._is_authenticated_user(user):
            return queryset.none()

        if KnowledgeBaseAccessService._has_global_access_for_operation(user, operation):
            return queryset

        operation_roles = KnowledgeBaseAccessService._get_operation_roles(operation)
        if operation == KnowledgeBaseAccessService.Operation.READ:
            return queryset.filter(
                Q(knowledge_base__visibility=KnowledgeBase.Visibility.SHARED)
                | Q(knowledge_base__owner=user)
                | Q(
                    knowledge_base__members__user=user,
                    knowledge_base__members__role__in=operation_roles,
                )
            ).distinct()

        return queryset.filter(
            Q(knowledge_base__owner=user)
            | Q(
                knowledge_base__members__user=user,
                knowledge_base__members__role__in=operation_roles,
            )
        ).distinct()

    @staticmethod
    def can_manage_documents(knowledge_base, user):
        return KnowledgeBaseAccessService.can_access(
            knowledge_base=knowledge_base,
            user=user,
            operation=KnowledgeBaseAccessService.Operation.CREATE,
        )

    @staticmethod
    def assert_can_manage_documents(knowledge_base, user):
        KnowledgeBaseAccessService.assert_can_access(
            knowledge_base=knowledge_base,
            user=user,
            operation=KnowledgeBaseAccessService.Operation.CREATE,
            message="Only knowledge base owner/editor can manage documents.",
        )

    @staticmethod
    def can_read_documents(knowledge_base, user):
        return KnowledgeBaseAccessService.can_access(
            knowledge_base=knowledge_base,
            user=user,
            operation=KnowledgeBaseAccessService.Operation.READ,
        )

    @staticmethod
    def assert_can_delete_documents(knowledge_base, user):
        KnowledgeBaseAccessService.assert_can_access(
            knowledge_base=knowledge_base,
            user=user,
            operation=KnowledgeBaseAccessService.Operation.DELETE,
            message="Only knowledge base owner/editor can delete documents.",
        )

    @staticmethod
    def can_assign_rights(knowledge_base, user):
        return KnowledgeBaseAccessService.can_access(
            knowledge_base=knowledge_base,
            user=user,
            operation=KnowledgeBaseAccessService.Operation.ASSIGN_RIGHTS,
        )

    @staticmethod
    def assert_can_assign_rights(knowledge_base, user):
        KnowledgeBaseAccessService.assert_can_access(
            knowledge_base=knowledge_base,
            user=user,
            operation=KnowledgeBaseAccessService.Operation.ASSIGN_RIGHTS,
            message="Only knowledge base owner can manage rights.",
        )

    @staticmethod
    def get_knowledge_base_or_default(data):
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


class DocumentService:
    @staticmethod
    def _resolve_knowledge_base(data):
        return KnowledgeBaseAccessService.get_knowledge_base_or_default(data)

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
        KnowledgeBaseAccessService.assert_can_delete_documents(
            knowledge_base=document.knowledge_base,
            user=actor_user,
        )
        document.soft_delete()
