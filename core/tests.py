from pathlib import Path

from django.test import TestCase

from core.dispatcher import SourceDispatcher


class SourceDispatcherSmokeTest(TestCase):
    def test_process_file_uses_repository_fixture(self):
        fixture_path = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "sample_dispatcher_input.txt"

        result = SourceDispatcher.process_file(str(fixture_path))

        self.assertEqual(result["text"], fixture_path.read_text(encoding="utf-8"))
        self.assertIn("chunks", result)
        self.assertGreaterEqual(len(result["chunks"]), 1)
        self.assertEqual(result["metadata"], {})
