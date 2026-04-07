from abc import ABC, abstractmethod

class BaseParser(ABC):

    @abstractmethod
    def parse(self, source):
        pass

    def normalize(self, text, metadata=None):
        return {"text": text,
                "metadata": metadata or {},
                "tables":[],
                "images":[],
                "source_type": self.__class__.__name__}
