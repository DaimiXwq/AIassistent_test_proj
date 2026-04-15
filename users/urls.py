from django.urls import path

from users.views import AdminUserCreateView, AdminUserDeactivateView, AdminUserRoleUpdateView

urlpatterns = [
    path("admin/users/", AdminUserCreateView.as_view(), name="admin-user-create"),
    path("admin/users/<int:user_id>/", AdminUserDeactivateView.as_view(), name="admin-user-deactivate"),
    path(
        "admin/users/<int:user_id>/role-access/",
        AdminUserRoleUpdateView.as_view(),
        name="admin-user-role-update",
    ),
]
