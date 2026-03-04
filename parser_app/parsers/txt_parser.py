from .base import BaseParser

class TXTParser(BaseParser):

    def parse(self, file_path):
        with open(file_path, encoding="utf-8") as f:
            text = f.read()
        return self.normalize(text)