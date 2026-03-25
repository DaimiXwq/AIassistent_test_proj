from django.db import models

# Create your models here.
class Document(models.Model):
    title = models.CharField(max_length=255)
    source = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Chunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="chunks")
    text = models.TextField()
    index = models.IntegerField()
    metadata = models.JSONField(default=dict)

class Embedding(models.Model):
    chunk = models.OneToOneField(Chunk, on_delete=models.CASCADE)
    vector = models.JSONField() # заменим на pgvector
