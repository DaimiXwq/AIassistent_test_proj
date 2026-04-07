from django.test import SimpleTestCase

from parser_app.parsers.factory import ParserFactory
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
