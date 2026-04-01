from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/parser/', include('parser_app.urls')),
    path('api/db/', include('db_server.urls')),
    path('api/core/', include('core.urls')),
    path('api/assistant/', include('ai_assistent_app.urls')),
]
