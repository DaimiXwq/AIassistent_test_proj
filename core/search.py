from db_server.models import Chunk, Embedding
from core.embeddings import EmbeddingService
import numpy as np

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    a_norm = np.linalg.norm(a)
    b_norm = np.linalg.norm(b)
    if a_norm == 0 or b_norm == 0:
        return 0.0
    return np.dot(a, b) / (a_norm * b_norm)

class SearchService:

    def __init__(self):
        self.embedding_service = EmbeddingService()

    def search(self, query, top_k=5):

        query_vector = self.embedding_service.generate(query)

        results = []

        embeddings = Embedding.objects.select_related("chunk", "chunk__document").filter(
            chunk__document__is_deleted=False
        )

        for emb in embeddings:
            score = cosine_similarity(query_vector, emb.vector)

            results.append({
                "text": emb.chunk.text,
                "score": float(score),
                "document_id": emb.chunk.document.id
            })

        results.sort(key=lambda x: x["score"], reverse=True)

        return results[:top_k]
