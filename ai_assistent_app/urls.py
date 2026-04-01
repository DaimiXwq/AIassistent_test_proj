from django.urls import path

from ai_assistent_app.views import OrchestrationView

urlpatterns = [
    path("orchestrate/", OrchestrationView.as_view(), name="orchestrate"),
]
