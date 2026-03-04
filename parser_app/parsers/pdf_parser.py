import fitz
from .base import BaseParser

class PDFParser(BaseParser):

    def parse(self, file_path):
        text = ""
        doc = fitz.open(file_path)

        for page in doc:
            text += page.get_text()

        return self.normalize(text)