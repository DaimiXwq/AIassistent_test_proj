from .pdf_parser import PDFParser
#from .docx_parser import DOCXParser
from .txt_parser import TXTParser
from .csv_parser import CSVParser

class ParserFactory:

    parsers = {
        "pdf": PDFParser,
        "docx": "DOCXParser",
        "txt": TXTParser,
        "csv": CSVParser,
        "cvs": CSVParser,
    }
    @classmethod
    def get_parser(cls, file_type):
        parser = cls.parsers.get(file_type.lower())
        if not parser:
            raise ValueError("Unsupported format")
        return parser()