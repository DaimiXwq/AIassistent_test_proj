from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from db_server.models import Document, KnowledgeBase, KnowledgeBaseMember


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

    def test_anonymous_document_list_excludes_personal_documents(self):
        url = reverse("db_server:list-documents")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        ids = {item["id"] for item in response.json()["results"]}
        self.assertIn(self.document_1.id, ids)
        self.assertNotIn(self.document_2.id, ids)

    def test_anonymous_document_retrieve_returns_404_for_personal_document(self):
        url = reverse("db_server:get-document", args=[self.document_2.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_document_delete_soft_deletes_document(self):
        url = reverse("db_server:get-document", args=[self.document_1.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        self.document_1.refresh_from_db()
        self.assertTrue(self.document_1.is_deleted)
        self.assertIsNotNone(self.document_1.deleted_at)


class KnowledgeBasePermissionTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(username="owner", password="pass1234")
        self.editor = user_model.objects.create_user(username="editor", password="pass1234")
        self.viewer = user_model.objects.create_user(username="viewer", password="pass1234")

        self.kb = KnowledgeBase.objects.create(
            name="Team KB",
            slug="team-kb",
            visibility=KnowledgeBase.Visibility.PERSONAL,
            owner=self.owner,
        )
        KnowledgeBaseMember.objects.create(
            knowledge_base=self.kb,
            user=self.editor,
            role=KnowledgeBaseMember.Role.EDITOR,
        )
        KnowledgeBaseMember.objects.create(
            knowledge_base=self.kb,
            user=self.viewer,
            role=KnowledgeBaseMember.Role.VIEWER,
        )

    def test_editor_can_create_document(self):
        self.client.force_login(self.editor)

        response = self.client.post(
            reverse("db_server:create-document-pipeline-result"),
            {
                "chunks": ["chunk-1", "chunk-2"],
                "title": "Editor doc",
                "knowledge_base_id": self.kb.id,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Document.objects.filter(knowledge_base=self.kb).count(), 1)

    def test_viewer_cannot_create_document(self):
        self.client.force_login(self.viewer)

        response = self.client.post(
            reverse("db_server:create-document-pipeline-result"),
            {
                "chunks": ["chunk-1"],
                "title": "Viewer doc",
                "knowledge_base_id": self.kb.id,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Document.objects.filter(knowledge_base=self.kb).count(), 0)

    def test_viewer_cannot_delete_document(self):
        document = Document.all_objects.create(
            title="Owner doc",
            source="manual",
            knowledge_base=self.kb,
            created_by=self.owner,
        )
        self.client.force_login(self.viewer)

        response = self.client.delete(reverse("db_server:get-document", args=[document.id]))

        self.assertEqual(response.status_code, 403)
        document.refresh_from_db()
        self.assertFalse(document.is_deleted)
