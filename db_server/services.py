from .models import Chunk, Document, Embedding
from core.embeddings import EmbeddingService


class DocumentService:
    @staticmethod
    def save_document(data):
        document = Document.objects.create(
            title=data.get("title") or "Uploaded Document",
            source=data.get("source") or "api",
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
