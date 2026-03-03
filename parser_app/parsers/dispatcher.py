import os
from parsers.factory import ParserFactory

class SourceDispatcher:

    @staticmethod
    def process(file_path):
        ext = os.path.splitext(file_path)[1][1:]
        parser = ParserFactory.get_parser(ext)
        return parser.parse(file_path)