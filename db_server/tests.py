from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from db_server.models import Document, KnowledgeBase


class DocumentSoftDeleteApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="tester", password="pass1234")
        self.kb_shared = KnowledgeBase.objects.create(
            name="Shared KB",
            slug="shared-kb",
            visibility=KnowledgeBase.Visibility.SHARED,
        )
        self.kb_personal = KnowledgeBase.objects.create(
            name="Personal KB",
            slug="personal-kb",
            visibility=KnowledgeBase.Visibility.PERSONAL,
            owner=self.user,
        )
        self.document_1 = Document.all_objects.create(
            title="Doc A",
            source="parser_api",
            knowledge_base=self.kb_shared,
        )
        self.document_2 = Document.all_objects.create(
            title="Doc B",
            source="manual",
            knowledge_base=self.kb_personal,
        )
        self.deleted_document = Document.all_objects.create(
            title="Doc Deleted",
            source="parser_api",
            knowledge_base=self.kb_shared,
            is_deleted=True,
        )

    def test_document_list_excludes_soft_deleted_and_applies_filters(self):
        url = reverse("db_server:list-documents")

        response = self.client.get(
            url,
            {
                "knowledge_base": self.kb_shared.id,
                "visibility": KnowledgeBase.Visibility.SHARED,
                "source": "parser_api",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(len(response.json()["results"]), 1)
        self.assertEqual(response.json()["results"][0]["id"], self.document_1.id)

    def test_document_retrieve_returns_404_for_soft_deleted(self):
        url = reverse("db_server:get-document", args=[self.deleted_document.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_document_delete_soft_deletes_document(self):
        url = reverse("db_server:get-document", args=[self.document_1.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        self.document_1.refresh_from_db()
        self.assertTrue(self.document_1.is_deleted)
        self.assertIsNotNone(self.document_1.deleted_at)
