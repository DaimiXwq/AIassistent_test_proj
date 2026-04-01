from django.contrib import admin
from django.urls import path

from core.views import ChunkTextView
from db_server.views import SaveDocumentAPIView, VectorSearchAPIView
from parser_app.views import ParseDocumentView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('parser/parse/', ParseDocumentView.as_view(), name='parser-parse'),
    path('core/chunk/', ChunkTextView.as_view(), name='core-chunk'),
    path('db/documents/', SaveDocumentAPIView.as_view(), name='db-save-document'),
    path('db/vector-search/', VectorSearchAPIView.as_view(), name='db-vector-search'),
]
