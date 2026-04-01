from django.urls import path

from ai_assistent_app.views import AssistantHealthView

app_name = "ai_assistent_app"

urlpatterns = [
    path("health/", AssistantHealthView.as_view(), name="health"),
]
