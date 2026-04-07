from .pdf_parser import PDFParser
from .docx_parser import DOCXParser
from .doc_parser import DOCParser
from .txt_parser import TXTParser
from .csv_parser import CSVParser
from .json_parser import JSONParser
from .markdown_parser import MarkdownParser
from .tsv_parser import TSVParser
from .djv_parser import DJVParser
from .xls_parser import XLSParser
from .xlsx_parser import XLSXParser
from .odt_parser import ODTParser
from .ods_parser import ODSParser

class ParserFactory:

    parsers = {
        "pdf": PDFParser,
        "docx": DOCXParser,
        "doc": DOCParser,
        "txt": TXTParser,
        "csv": CSVParser,
        "json": JSONParser,
        "md": MarkdownParser,
        "markdown": MarkdownParser,
        "tsv": TSVParser,
        "djv": DJVParser,
        "xls": XLSParser,
        "xlsx": XLSXParser,
        "odt": ODTParser,
        "ods": ODSParser,
    }
    @classmethod
    def get_parser(cls, file_type):
        parser = cls.parsers.get(file_type.lower())
        if not parser:
            raise ValueError("Unsupported format")
        return parser()
