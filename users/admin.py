from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.exceptions import PermissionDenied

from users.models import UserProfile
from users.permissions import is_admin_user, is_head_of_department_user

User = get_user_model()


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "group_type", "access_level")
    search_fields = ("user__username", "user__email")
    list_filter = ("group_type", "access_level")

    def has_add_permission(self, request):
        return is_admin_user(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_admin_user(request.user)

    def get_readonly_fields(self, request, obj=None):
        if is_admin_user(request.user):
            return ()
        return ("group_type", "access_level", "user")

    def save_model(self, request, obj, form, change):
        if not is_admin_user(request.user):
            raise PermissionDenied("Only admin can assign group type or access level.")
        super().save_model(request, obj, form, change)


class UserAdmin(BaseUserAdmin):
    def has_add_permission(self, request):
        return is_admin_user(request.user) or is_head_of_department_user(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_admin_user(request.user)

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if not is_admin_user(request.user):
            readonly.extend(["is_active", "is_staff", "is_superuser", "groups", "user_permissions"])
        return tuple(dict.fromkeys(readonly))

    def save_model(self, request, obj, form, change):
        if not is_admin_user(request.user) and not is_head_of_department_user(request.user):
            raise PermissionDenied("Only admin or head_of_department can create users.")

        if not is_admin_user(request.user):
            if change:
                raise PermissionDenied("Only admin can edit existing users.")
            obj.is_staff = False
            obj.is_superuser = False

        super().save_model(request, obj, form, change)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
