from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q

from db_server.models import Document, KnowledgeBase
from db_server.services import DocumentService, KnowledgeBaseAccessService


class DocumentListView(APIView):
    SORT_FIELDS = {"created_at", "title", "source", "id"}

    def get(self, request):
        queryset = Document.objects.select_related("knowledge_base")
        user = request.user if request.user.is_authenticated else None

        if user is None:
            queryset = queryset.filter(knowledge_base__visibility=KnowledgeBase.Visibility.SHARED)
        else:
            queryset = queryset.filter(
                Q(knowledge_base__visibility=KnowledgeBase.Visibility.SHARED)
                | Q(knowledge_base__owner=user)
                | Q(
                    knowledge_base__members__user=user,
                    knowledge_base__members__role__in=KnowledgeBaseAccessService.READ_ROLES,
                )
            ).distinct()

        knowledge_base_id = request.query_params.get("knowledge_base")
        if knowledge_base_id:
            queryset = queryset.filter(knowledge_base_id=knowledge_base_id)

        visibility = request.query_params.get("visibility")
        if visibility:
            queryset = queryset.filter(knowledge_base__visibility=visibility)

        source = request.query_params.get("source")
        if source:
            queryset = queryset.filter(source=source)

        sort_by = request.query_params.get("sort_by", "created_at")
        if sort_by not in self.SORT_FIELDS:
            return Response(
                {"error": f"Invalid sort_by. Allowed values: {', '.join(sorted(self.SORT_FIELDS))}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        sort_order = request.query_params.get("sort_order", "desc")
        if sort_order not in {"asc", "desc"}:
            return Response(
                {"error": "Invalid sort_order. Allowed values: asc, desc."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ordering = sort_by if sort_order == "asc" else f"-{sort_by}"
        queryset = queryset.order_by(ordering, "-id")

        try:
            page = max(int(request.query_params.get("page", 1)), 1)
            page_size = min(max(int(request.query_params.get("page_size", 20)), 1), 100)
        except ValueError:
            return Response(
                {"error": "page and page_size must be integers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total = queryset.count()
        offset = (page - 1) * page_size
        documents = queryset[offset : offset + page_size]

        return Response(
            {
                "count": total,
                "page": page,
                "page_size": page_size,
                "results": [
                    {
                        "id": document.id,
                        "title": document.title,
                        "source": document.source,
                        "created_at": document.created_at,
                        "knowledge_base_id": document.knowledge_base_id,
                        "visibility": document.knowledge_base.visibility,
                        "owner_id": document.knowledge_base.owner_id,
                    }
                    for document in documents
                ],
            },
            status=status.HTTP_200_OK,
        )


class DocumentPipelineResultCreateView(APIView):
    def post(self, request):
        chunks = request.data.get("chunks")

        if not isinstance(chunks, list) or not chunks:
            return Response(
                {"error": "'chunks' must be a non-empty list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload = {
            "chunks": chunks,
            "title": request.data.get("title"),
            "source": request.data.get("source"),
            "knowledge_base_id": request.data.get("knowledge_base_id"),
            "created_by": request.user if request.user.is_authenticated else None,
            "actor_user": request.user if request.user.is_authenticated else None,
        }
        document = DocumentService.save_document(payload)

        return Response(
            {
                "document_id": document.id,
                "chunks_count": len(chunks),
                "knowledge_base_id": document.knowledge_base_id,
                "visibility": document.knowledge_base.visibility,
                "owner_id": document.knowledge_base.owner_id,
            },
            status=status.HTTP_201_CREATED,
        )


class DocumentRetrieveView(APIView):
    def get(self, request, document_id):
        document = Document.objects.filter(id=document_id).prefetch_related("chunks").first()

        if document is None:
            return Response(
                {"error": "Document not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        actor_user = request.user if request.user.is_authenticated else None
        if not KnowledgeBaseAccessService.can_read_documents(document.knowledge_base, actor_user):
            return Response(
                {"error": "Document not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "id": document.id,
                "title": document.title,
                "source": document.source,
                "created_at": document.created_at,
                "knowledge_base_id": document.knowledge_base_id,
                "visibility": document.knowledge_base.visibility,
                "owner_id": document.knowledge_base.owner_id,
                "chunks": [
                    {
                        "id": chunk.id,
                        "index": chunk.index,
                        "text": chunk.text,
                        "metadata": chunk.metadata,
                    }
                    for chunk in document.chunks.order_by("index")
                ],
            },
            status=status.HTTP_200_OK,
        )
    def delete(self, request, document_id):
        document = Document.all_objects.filter(id=document_id).first()

        if document is None or document.is_deleted:
            return Response(
                {"error": "Document not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        DocumentService.soft_delete_document(
            document=document,
            actor_user=request.user if request.user.is_authenticated else None,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
