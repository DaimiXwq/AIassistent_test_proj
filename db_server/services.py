from .models import Document, Chunk

class DocumentService:

    @staticmethod
    def save_document(data):

        document = Document.objects.create(
            title="Uploaded Document",
            source="api"
        )

        chunks = []

        for i, chunk_text in enumerate(data["chunks"]):
            chunk = Chunk.objects.create(
                document=document,
                text=chunk_text,
                index=i
            )
            chunks.append(chunk)
        
        return document