from django.urls import path

from db_server.views import (
    DocumentListView,
    DocumentPipelineResultCreateView,
    DocumentRetrieveView,
)

app_name = "db_server"

urlpatterns = [
    path("documents/", DocumentListView.as_view(), name="list-documents"),
    path(
        "documents/pipeline-result/",
        DocumentPipelineResultCreateView.as_view(),
        name="create-document-pipeline-result",
    ),
    path("documents/<int:document_id>/", DocumentRetrieveView.as_view(), name="get-document"),
]
