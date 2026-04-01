import requests
from django.conf import settings

from .exceptions import InternalAPIError


class CoreAPIClient:
    def __init__(self, base_url=None, timeout=None):
        self.base_url = (base_url or settings.CORE_API_BASE_URL).rstrip("/")
        self.timeout = timeout or settings.INTERNAL_API_TIMEOUT_SECONDS

    def chunk_text(self, text, metadata=None):
        payload = {
            "text": text,
            "metadata": metadata or {},
        }
        return self._request("post", "/core/chunk/", json=payload)

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
                code="core_api_unavailable",
                message="Core API is unavailable",
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
                code="core_api_bad_response",
                message="Core API returned a non-success status",
                details={"status_code": response.status_code, "response": details},
                status_code=502,
            )

        try:
            return response.json()
        except ValueError as exc:
            raise InternalAPIError(
                code="core_api_invalid_json",
                message="Core API returned invalid JSON",
                details={"raw": response.text},
                status_code=502,
            ) from exc
