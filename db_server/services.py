from .models import Document, Chunk, Embedding
from core.embeddings import EmbeddingService

class DocumentService:

    @staticmethod
    def save_document(data):

        document = Document.objects.create(
            title="Uploaded Document",
            source="api"
        )

        chunks = []
        embedding_service = EmbeddingService()

        for i, chunk_text in enumerate(data["chunks"]):
            chunk = Chunk.objects.create(
                document=document,
                text=chunk_text,
                index=i
            )
            chunks.append(chunk)

            vector = embedding_service.generate(chunk_text)

            Embedding.objects.create(
                chunk=chunk,
                vector=vector
            )
        
        return document