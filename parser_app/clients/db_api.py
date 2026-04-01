import requests
from django.conf import settings

from .exceptions import InternalAPIError


class DBAPIClient:
    def __init__(self, base_url=None, timeout=None):
        self.base_url = (base_url or settings.DB_API_BASE_URL).rstrip("/")
        self.timeout = timeout or settings.INTERNAL_API_TIMEOUT_SECONDS

    def save_document(self, title, source, chunks):
        payload = {
            "title": title,
            "source": source,
            "chunks": chunks,
        }
        return self._request("post", "/db/documents/", json=payload)

    def vector_search(self, query_vector, top_k=5):
        payload = {
            "query_vector": query_vector,
            "top_k": top_k,
        }
        return self._request("post", "/db/vector-search/", json=payload)

    def _request(self, method, path, **kwargs):
        try:
            response = requests.request(
                method,
                f"{self.base_url}{path}",
                timeout=self.timeout,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise InternalAPIError(
                code="db_api_unavailable",
                message="DB API is unavailable",
                details={"reason": str(exc)},
                status_code=502,
            ) from exc

        if not response.ok:
            details = {}
            try:
                details = response.json()
            except ValueError:
                details = {"raw": response.text}
            raise InternalAPIError(
                code="db_api_bad_response",
                message="DB API returned a non-success status",
                details={"status_code": response.status_code, "response": details},
                status_code=502,
            )

        try:
            return response.json()
        except ValueError as exc:
            raise InternalAPIError(
                code="db_api_invalid_json",
                message="DB API returned invalid JSON",
                details={"raw": response.text},
                status_code=502,
            ) from exc
