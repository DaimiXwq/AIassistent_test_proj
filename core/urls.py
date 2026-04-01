from django.urls import path

from core.views import SemanticSearchView

urlpatterns = [
    path("semantic-search/", SemanticSearchView.as_view(), name="semantic-search"),
]
