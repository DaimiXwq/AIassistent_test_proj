from .pdf_parser import PDFParser
from .docx_parser import DOCXParser
from .txt_parser import TXTParser
from .csv_parser import CSVParser
from .json_parser import JSONParser
from .markdown_parser import MarkdownParser
from .tsv_parser import TSVParser

class ParserFactory:

    parsers = {
        "pdf": PDFParser,
        "docx": DOCXParser,
        "txt": TXTParser,
        "csv": CSVParser,
        "json": JSONParser,
        "md": MarkdownParser,
        "markdown": MarkdownParser,
        "tsv": TSVParser,
    }
    @classmethod
    def get_parser(cls, file_type):
        parser = cls.parsers.get(file_type.lower())
        if not parser:
            raise ValueError("Unsupported format")
        return parser()
