from django.test import TestCase
from unittest.mock import patch

from core.search import SearchService
from db_server.models import Chunk, Document, Embedding, KnowledgeBase

class StartPageViewTests(TestCase):
    def test_root_returns_start_page(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "start_page.html")
        self.assertContains(response, "AI Assistant Platform")


class SearchServiceSoftDeleteTests(TestCase):
    @patch("core.search.EmbeddingService.generate")
    def test_search_skips_embeddings_for_soft_deleted_documents(self, mocked_generate):
        mocked_generate.return_value = [1.0, 0.0]

        kb = KnowledgeBase.objects.create(
            name="Shared",
            slug="shared-search-kb",
            visibility=KnowledgeBase.Visibility.SHARED,
        )
        active_document = Document.all_objects.create(title="Active", source="api", knowledge_base=kb)
        deleted_document = Document.all_objects.create(
            title="Deleted",
            source="api",
            knowledge_base=kb,
            is_deleted=True,
        )

        active_chunk = Chunk.objects.create(document=active_document, text="active chunk", index=0)
        deleted_chunk = Chunk.objects.create(document=deleted_document, text="deleted chunk", index=0)
        Embedding.objects.create(chunk=active_chunk, vector=[1.0, 0.0])
        Embedding.objects.create(chunk=deleted_chunk, vector=[1.0, 0.0])

        results = SearchService().search(query="test", top_k=10)
        document_ids = {item["document_id"] for item in results}

        self.assertIn(active_document.id, document_ids)
        self.assertNotIn(deleted_document.id, document_ids)
