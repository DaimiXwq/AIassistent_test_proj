from rest_framework.permissions import BasePermission


class IsActiveUser(BasePermission):
    message = "User account is disabled."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return True
        return user.is_active
