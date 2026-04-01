"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from parser_app.views import ParseDocumentView
from db_server.views import SaveDocumentView
from core.views import SearchView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/parse/", ParseDocumentView.as_view(), name="parse-document"),
    path("api/v1/documents/save/", SaveDocumentView.as_view(), name="save-document"),
    path("api/v1/search/", SearchView.as_view(), name="search"),
]
