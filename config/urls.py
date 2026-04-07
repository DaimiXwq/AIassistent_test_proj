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
from django.urls import include, path

from core.views import ManualTestPageView, StartPageView

urlpatterns = [
    path("", StartPageView.as_view(), name="start-page"),
    path("manual-test/", ManualTestPageView.as_view(), name="manual-test"),
    path("admin/", admin.site.urls),
    path("api/parser/", include(("parser_app.urls", "parser_app"), namespace="parser_app")),
    path("api/db/", include(("db_server.urls", "db_server"), namespace="db_server")),
    path("api/core/", include(("core.urls", "core"), namespace="core")),
    path(
        "api/assistant/",
        include(("ai_assistent_app.urls", "ai_assistent_app"), namespace="ai_assistent_app"),
    ),
]
