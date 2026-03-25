import os
from parser_app.parsers.factory import ParserFactory

class SourceDispatcher:

    @staticmethod
    def process_file(file_path):
        ext = os.path.splitext(file_path)[1][1:]
        parser = ParserFactory.get_parser(ext)

        result = parser.parse(file_path)

        return SourceDispatcher._postprocess(result)

    @staticmethod
    def _postprocess(data):
        #
        # - чистим текст
        # - разбиваем на чанки
        return data