from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.search import SearchService


class SearchView(APIView):
    def post(self, request):
        query = request.data.get("query")
        top_k = request.data.get("top_k", 5)

        if not query:
            return Response(
                {"error": "'query' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            top_k = int(top_k)
        except (TypeError, ValueError):
            return Response(
                {"error": "'top_k' must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = SearchService().search(query=query, top_k=top_k)
        return Response({"results": results}, status=status.HTTP_200_OK)
