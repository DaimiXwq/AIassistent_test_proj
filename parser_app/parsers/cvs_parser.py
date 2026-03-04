import pandas as pd
from .base import BaseParser

class CSVParser(BaseParser):

    def parse(self, file_path):
        df = pd.read_csv(file_path)
        return  {"text": df.to_string(),
                "metadata": {"row": len(df)},
                "tables":[df.to_dict()],
                "images":[],
                "source_type": "csv"}