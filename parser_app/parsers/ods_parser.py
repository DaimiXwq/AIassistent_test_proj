import pandas as pd

from .base import BaseParser


class ODSParser(BaseParser):
    def parse(self, file_path):
        df = pd.read_excel(file_path)
        return {
            "text": df.to_string(),
            "metadata": {"row": len(df), "format": "ods"},
            "tables": [df.to_dict()],
            "images": [],
            "source_type": "ods",
        }
