import numpy as np
from sentence_transformers import SentenceTransformer

class EmbeddingService:

    def generate(self, text):
        return np.random.rand(384).tolist()

class EmbeddingServiceTransformers(EmbeddingService):

    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6_v2')

    def generate(self, text):
        return self.model.encode(text)
