class InternalAPIError(Exception):
    def __init__(self, code, message, details=None, status_code=None):
        self.code = code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)


def normalize_exception(exc):
    if isinstance(exc, InternalAPIError):
        return {
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        }, exc.status_code or 500

    return {
        "error": {
            "code": "internal_error",
            "message": str(exc),
            "details": {},
        }
    }, 500
