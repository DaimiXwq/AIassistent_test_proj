from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.errors import build_error_response
from core.search import SearchService
from core.serializers import (
    SearchRequestSerializer,
    SearchResponseSerializer,
    SearchResultItemSerializer,
)


class SearchView(APIView):

    def post(self, request):
        request_serializer = SearchRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        try:
            data = request_serializer.validated_data
            results = SearchService().search(data["query"], top_k=data["top_k"])

            item_serializer = SearchResultItemSerializer(data=results, many=True)
            item_serializer.is_valid(raise_exception=True)

            response_serializer = SearchResponseSerializer(data={"results": item_serializer.data})
            response_serializer.is_valid(raise_exception=True)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            return build_error_response(
                code="search_failed",
                message="Search failed",
                details={"error": str(exc)},
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
