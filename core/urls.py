from django.urls import path

from core.views import ChunkTextView, ManualTestPageView, SearchView

app_name = "core"

urlpatterns = [
    path("manual-test/", ManualTestPageView.as_view(), name="manual-test"),
    path("search/", SearchView.as_view(), name="search"),
    path("chunk/", ChunkTextView.as_view(), name="chunk"),
]
