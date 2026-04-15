import re

class SmatChunker:

    def __init__(self, max_lenght=500):
        self.max_lenght = max_lenght

    def split_text(self, text):
        sentences = re.split(r'(?<=[.!?]) +', text)

        chunks = []
        current = ""

        for sentence in sentences:
            if len(current) + len(sentence) < self.max_lenght:
                current += " " + sentence
            else:
                if current.strip():
                    chunks.append(current.strip())
                current = sentence
        
        if current: chunks.append(current.strip())

        return chunks

class TextChunker:

    def __init__(self, max_lenght=500, overlap=50):
        self.max_lenght = max_lenght
        self.overlap = overlap

    def split_text(self, text):
        chunks = []
        start = 0

        while start<len(text):
            end = start + self.max_lenght
            chunk = text[start:end]

            chunks.append(chunk)

            start += self.max_lenght - self.overlap

        return chunks
