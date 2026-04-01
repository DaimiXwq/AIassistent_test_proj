from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_assistent_app.serializers import OrchestrateRequestSerializer, OrchestrateResponseSerializer
from core.search import SearchService
from db_server.models import Document
from db_server.views import DocumentViewSet


class OrchestrationView(APIView):
    """Orchestrates user request via core search and db document APIs."""

    def post(self, request):
        serializer = OrchestrateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        query = serializer.validated_data["query"]
        top_k = serializer.validated_data["top_k"]
        document_id = serializer.validated_data.get("document_id")

        matches = SearchService().search(query=query, top_k=top_k)

        document_payload = None
        if document_id is not None:
            document = Document.objects.filter(pk=document_id).first()
            if not document:
                return Response(
                    {"detail": "Document not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            document_payload = DocumentViewSet()._document_payload(document)

        payload = {
            "query": query,
            "top_k": top_k,
            "matches": matches,
            "document": document_payload,
        }
        response_serializer = OrchestrateResponseSerializer(payload)

        return Response(response_serializer.data, status=status.HTTP_200_OK)
