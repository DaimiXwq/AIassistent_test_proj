from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def build_error_response(code, message, details=None, http_status=status.HTTP_400_BAD_REQUEST):
    payload = {
        "code": code,
        "message": message,
        "details": details or {},
    }
    return Response(payload, status=http_status)


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return build_error_response(
            code="internal_error",
            message="Internal server error",
            details={"error": str(exc)},
            http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    detail = response.data
    return build_error_response(
        code="request_error",
        message="Request failed",
        details=detail,
        http_status=response.status_code,
    )
