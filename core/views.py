from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.chunker import SmatChunker
from core.search import SearchService
from users.authentication import DEFAULT_API_AUTHENTICATION_CLASSES
from users.drf_permissions import IsActiveUser
from users.permissions import is_admin_user, is_head_of_department_user


class SearchView(APIView):
    authentication_classes = DEFAULT_API_AUTHENTICATION_CLASSES
    permission_classes = [IsAuthenticated, IsActiveUser]

    def post(self, request):
        query = request.data.get("query")
        top_k = request.data.get("top_k", 5)

        if not query:
            return Response(
                {"error": "Поле 'query' обязательно для заполнения."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            top_k = int(top_k)
        except (TypeError, ValueError):
            return Response(
                {"error": "Поле 'top_k' должно быть целым числом."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if top_k <= 0:
            return Response(
                {"error": "Поле 'top_k' должно быть больше 0."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = SearchService().search(query=query, user=request.user, top_k=top_k)
        return Response({"results": results}, status=status.HTTP_200_OK)


class ChunkTextView(APIView):
    authentication_classes = DEFAULT_API_AUTHENTICATION_CLASSES
    permission_classes = [IsAuthenticated, IsActiveUser]

    def post(self, request):
        text = request.data.get("text")

        if not isinstance(text, str) or not text.strip():
            return Response(
                {"error": "Поле 'text' должно быть непустой строкой."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        chunker = SmatChunker()
        chunks = chunker.split_text(text)
        return Response(
            {
                "chunks": chunks,
                "metadata": request.data.get("metadata", {}),
            },
            status=status.HTTP_200_OK,
        )


class ManualTestPageView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "manual_test.html"
    login_url = "/admin/login/"

    def test_func(self):
        return is_admin_user(self.request.user) or is_head_of_department_user(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = getattr(self.request.user, "profile", None)
        context["current_user"] = {
            "username": self.request.user.username,
            "group_type": getattr(profile, "group_type", "—"),
            "access_level": getattr(profile, "access_level", "—"),
        }
        context["can_create_users"] = is_admin_user(self.request.user) or is_head_of_department_user(
            self.request.user
        )
        context["can_manage_roles"] = is_admin_user(self.request.user)
        context["can_delete_users"] = is_admin_user(self.request.user)
        return context


class StartPageView(TemplateView):
    template_name = "start_page.html"
