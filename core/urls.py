from django.urls import path

from core.views import ChunkTextView, SearchView

app_name = "core"

urlpatterns = [
    path("search/", SearchView.as_view(), name="search"),
    path("chunk/", ChunkTextView.as_view(), name="chunk"),
]
