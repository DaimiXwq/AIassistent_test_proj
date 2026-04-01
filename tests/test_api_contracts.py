from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient


class APIContractsSmokeTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_parse_result_contract(self):
        file = SimpleUploadedFile("sample.txt", b"Hello world. This is a test.", content_type="text/plain")

        response = self.client.post("/api/v1/parse/", {"file": file}, format="multipart")

        self.assertEqual(response.status_code, 200)
        self.assertSetEqual(set(response.data.keys()), {"text", "chunks", "metadata"})
        self.assertIsInstance(response.data["text"], str)
        self.assertIsInstance(response.data["chunks"], list)
        self.assertIsInstance(response.data["metadata"], dict)

    def test_save_document_contract(self):
        payload = {
            "text": "Hello world.",
            "chunks": ["Hello world."],
            "metadata": {"source": "smoke"},
        }

        response = self.client.post("/api/v1/documents/save/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertSetEqual(set(response.data.keys()), {"document_id", "chunks_count", "status"})
        self.assertIsInstance(response.data["document_id"], int)
        self.assertEqual(response.data["chunks_count"], 1)
        self.assertEqual(response.data["status"], "saved")

    def test_search_result_contract(self):
        save_payload = {
            "text": "Python testing document",
            "chunks": ["Python testing document"],
            "metadata": {},
        }
        self.client.post("/api/v1/documents/save/", save_payload, format="json")

        response = self.client.post("/api/v1/search/", {"query": "Python", "top_k": 1}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertGreaterEqual(len(response.data["results"]), 1)

        item = response.data["results"][0]
        self.assertSetEqual(set(item.keys()), {"text", "score", "document_id"})
        self.assertIsInstance(item["text"], str)
        self.assertIsInstance(item["score"], float)
        self.assertIsInstance(item["document_id"], int)

    def test_error_envelope_contract(self):
        response = self.client.post("/api/v1/search/", {}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertSetEqual(set(response.data.keys()), {"code", "message", "details"})
