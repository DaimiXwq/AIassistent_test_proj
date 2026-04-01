from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.search import SearchService
from core.serializers import SemanticSearchRequestSerializer, SemanticSearchResponseSerializer


class SemanticSearchView(APIView):
    """Semantic search endpoint for query/top_k."""

    def post(self, request):
        serializer = SemanticSearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        query = serializer.validated_data["query"]
        top_k = serializer.validated_data["top_k"]

        matches = SearchService().search(query=query, top_k=top_k)
        response_payload = {
            "query": query,
            "top_k": top_k,
            "matches": matches,
        }
        response_serializer = SemanticSearchResponseSerializer(response_payload)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
