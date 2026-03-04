from docx import Document
from .base import BaseParser

class DOCXParser(BaseParser):

    def parse(self, file_path):
        doc = Document(file_path)
        text = "\n".join(p.text for p in doc.paragraphs)
        return self.normalize(text)