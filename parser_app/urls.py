from django.urls import path

from parser_app.views import ParseDocumentView

app_name = "parser_app"

urlpatterns = [
    path("parse/", ParseDocumentView.as_view(), name="parse-document"),
]
