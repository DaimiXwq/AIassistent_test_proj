from unittest import mock

from django.test import SimpleTestCase

from parser_app.parsers.doc_parser import DOCParser
from parser_app.parsers.factory import ParserFactory
from parser_app.parsers.formats import SUPPORTED_FORMATS
from parser_app.parsers.json_parser import JSONParser
from parser_app.parsers.markdown_parser import MarkdownParser
from parser_app.parsers.tsv_parser import TSVParser


class ParserFactoryTests(SimpleTestCase):
    def test_factory_supports_new_formats(self):
        self.assertIsInstance(ParserFactory.get_parser("json"), JSONParser)
        self.assertIsInstance(ParserFactory.get_parser("md"), MarkdownParser)
        self.assertIsInstance(ParserFactory.get_parser("markdown"), MarkdownParser)
        self.assertIsInstance(ParserFactory.get_parser("tsv"), TSVParser)

    def test_factory_raises_for_unsupported_format(self):
        with self.assertRaises(ValueError):
            ParserFactory.get_parser("exe")

    def test_factory_parsers_match_supported_formats(self):
        self.assertSetEqual(set(ParserFactory.parsers.keys()), set(SUPPORTED_FORMATS))


class DOCParserTests(SimpleTestCase):
    def test_cleanup_text_removes_binary_garbage(self):
        parser = DOCParser()

        dirty = "\x00\x02\x03Test line\n\x07\x08\n12345\n"
        cleaned = parser._cleanup_text(dirty)

        self.assertEqual(cleaned, "Test line\n12345")

    def test_parse_falls_back_to_heuristic_when_antiword_missing(self):
        parser = DOCParser()

        fake_raw = "Привет мир".encode("cp1251") + b"\x00\x01\x02"
        with mock.patch.object(parser, "_extract_with_antiword", return_value=""):
            with mock.patch("builtins.open", mock.mock_open(read_data=fake_raw)):
                result = parser.parse("/tmp/dummy.doc")

        self.assertIn("Привет мир", result["text"])
        self.assertEqual(result["metadata"], {"format": "doc"})
