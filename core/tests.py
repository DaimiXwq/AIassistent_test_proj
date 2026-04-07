from django.test import TestCase


class StartPageViewTests(TestCase):
    def test_root_returns_start_page(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "start_page.html")
        self.assertContains(response, "AI Assistant Platform")
