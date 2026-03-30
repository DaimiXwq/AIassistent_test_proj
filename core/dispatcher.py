import os
from parser_app.parsers.factory import ParserFactory
from core.chunker import SmatChunker, TextChunker

class SourceDispatcher:

    @staticmethod
    def process_file(file_path):
        ext = os.path.splitext(file_path)[1][1:]
        parser = ParserFactory.get_parser(ext)

        result = parser.parse(file_path)

        return SourceDispatcher._postprocess(result)

    @staticmethod
    def _postprocess(data):
        chunker = SmatChunker()
        chunks = chunker.split_text(data["text"])
        return {
            "text": data["text"],
            "chunks": chunks,
            "metadata":data["metadata"]
            }