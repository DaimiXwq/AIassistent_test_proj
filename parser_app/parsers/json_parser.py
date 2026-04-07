import json

from .base import BaseParser


class JSONParser(BaseParser):
    def parse(self, file_path):
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        text = json.dumps(data, ensure_ascii=False, indent=2)
        metadata = {
            "root_type": type(data).__name__,
            "items_count": len(data) if isinstance(data, (list, dict)) else 1,
        }
        return self.normalize(text, metadata=metadata)
