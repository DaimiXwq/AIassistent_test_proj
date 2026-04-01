from core.embeddings import EmbeddingService
from parser_app.clients.db_api import DBAPIClient


class SearchService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.db_api = DBAPIClient()

    def search(self, query, top_k=5):
        query_vector = self.embedding_service.generate(query)
        response = self.db_api.vector_search(query_vector=query_vector, top_k=top_k)
        return response.get("results", [])
