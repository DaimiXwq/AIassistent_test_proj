import pandas as pd

from .base import BaseParser


class TSVParser(BaseParser):
    def parse(self, file_path):
        df = pd.read_csv(file_path, sep="\t")
        return {
            "text": df.to_string(),
            "metadata": {"row": len(df), "separator": "tab"},
            "tables": [df.to_dict()],
            "images": [],
            "source_type": "tsv",
        }
