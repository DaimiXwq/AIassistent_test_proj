from rest_framework.authentication import BasicAuthentication, SessionAuthentication


class SessionAuthentication401(SessionAuthentication):
    def authenticate_header(self, request):
        return "Session"


DEFAULT_API_AUTHENTICATION_CLASSES = [SessionAuthentication401, BasicAuthentication]
