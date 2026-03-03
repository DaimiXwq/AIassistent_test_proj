from abc import ABC, abstractclassmethod

class BaseParser(ABC):

    @abstractclassmethod
    def parse(self, sourse):
        pass

    def normalize(self, text, metadata=None):
        return {"text": text,
                "metadata": metadata or {},
                "tables":[],
                "images":[],
                "source_type": self.__class__.__name__}
