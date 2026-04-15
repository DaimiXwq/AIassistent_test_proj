from .models import Chunk, Document, Embedding, KnowledgeBase
from core.embeddings import EmbeddingService


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
