from django.urls import path

from parser_app.views import ParseDocumentView

urlpatterns = [
    path("parse/", ParseDocumentView.as_view(), name="parse-document"),
]
