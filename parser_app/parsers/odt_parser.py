from .base import BaseParser


class ODTParser(BaseParser):
    def parse(self, file_path):
        with open(file_path, "rb") as f:
            raw = f.read()

        text = raw.decode("utf-8", errors="ignore")
        return self.normalize(text, metadata={"format": "odt"})
