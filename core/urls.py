from django.urls import path

from core.views import SearchView

app_name = "core"

urlpatterns = [
    path("search/", SearchView.as_view(), name="search"),
]
