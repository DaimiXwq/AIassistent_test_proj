from .csv_parser import CSVParser
from .djvu_parser import DJVUParser
from .doc_parser import DOCParser
from .docx_parser import DOCXParser
from .formats import SUPPORTED_FORMATS
from .json_parser import JSONParser
from .markdown_parser import MarkdownParser
from .ods_parser import ODSParser
from .odt_parser import ODTParser
from .pdf_parser import PDFParser
from .tsv_parser import TSVParser
from .txt_parser import TXTParser
from .xls_parser import XLSParser
from .xlsx_parser import XLSXParser

AVAILABLE_PARSERS = {
    "pdf": PDFParser,
    "docx": DOCXParser,
    "doc": DOCParser,
    "txt": TXTParser,
    "csv": CSVParser,
    "json": JSONParser,
    "md": MarkdownParser,
    "markdown": MarkdownParser,
    "tsv": TSVParser,
    "djvu": DJVUParser,
    "xls": XLSParser,
    "xlsx": XLSXParser,
    "odt": ODTParser,
    "ods": ODSParser,
}


class ParserFactory:
    parsers = {
        file_extension: AVAILABLE_PARSERS[file_extension]
        for file_extension in SUPPORTED_FORMATS
    }

    @classmethod
    def get_parser(cls, file_type):
        parser = cls.parsers.get(file_type.lower())
        if not parser:
            raise ValueError("Unsupported format")
        return parser()
