import pandas as pd

from .base import BaseParser


class XLSParser(BaseParser):
    def parse(self, file_path):
        df = pd.read_excel(file_path)
        return {
            "text": df.to_string(),
            "metadata": {"row": len(df), "format": "xls"},
            "tables": [df.to_dict()],
            "images": [],
            "source_type": "xls",
        }
