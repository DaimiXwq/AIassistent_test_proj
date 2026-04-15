from django.contrib.auth import get_user_model
from django.test import TestCase

from users.constants import (
    ACCESS_LEVEL_1,
    ACCESS_LEVEL_2,
    ACCESS_LEVEL_4,
    ACCESS_LEVEL_ADMIN,
    GROUP_TYPE_ADMIN,
    GROUP_TYPE_HEAD_OF_DEPARTMENT,
    GROUP_TYPE_STANDARD,
)

User = get_user_model()


class AdminUserManagementApiTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="admin_user", password="StrongPass123!")
        self.admin.profile.group_type = GROUP_TYPE_ADMIN
        self.admin.profile.access_level = ACCESS_LEVEL_ADMIN
        self.admin.profile.save()

        self.hod = User.objects.create_user(username="hod_user", password="StrongPass123!")
        self.hod.profile.group_type = GROUP_TYPE_HEAD_OF_DEPARTMENT
        self.hod.profile.access_level = ACCESS_LEVEL_2
        self.hod.profile.save()

        self.standard = User.objects.create_user(username="standard_user", password="StrongPass123!")
        self.standard.profile.group_type = GROUP_TYPE_STANDARD
        self.standard.profile.access_level = ACCESS_LEVEL_4
        self.standard.profile.save()

    def test_admin_can_create_user_with_custom_group_and_access(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            "/api/users/admin/users/",
            {
                "username": "created_by_admin",
                "password": "StrongPass123!",
                "group_type": GROUP_TYPE_HEAD_OF_DEPARTMENT,
                "access_level": ACCESS_LEVEL_1,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        created = User.objects.get(username="created_by_admin")
        self.assertEqual(created.profile.group_type, GROUP_TYPE_HEAD_OF_DEPARTMENT)
        self.assertEqual(created.profile.access_level, ACCESS_LEVEL_1)

    def test_head_of_department_can_create_only_standard_users(self):
        self.client.force_login(self.hod)

        response = self.client.post(
            "/api/users/admin/users/",
            {
                "username": "created_by_hod",
                "password": "StrongPass123!",
                "group_type": GROUP_TYPE_STANDARD,
                "access_level": ACCESS_LEVEL_4,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        created = User.objects.get(username="created_by_hod")
        self.assertEqual(created.profile.group_type, GROUP_TYPE_STANDARD)

    def test_head_of_department_cannot_escalate_new_user_role(self):
        self.client.force_login(self.hod)

        response = self.client.post(
            "/api/users/admin/users/",
            {
                "username": "created_with_admin_role",
                "password": "StrongPass123!",
                "group_type": GROUP_TYPE_ADMIN,
                "access_level": ACCESS_LEVEL_ADMIN,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_only_admin_can_deactivate_user(self):
        self.client.force_login(self.hod)
        response = self.client.delete(f"/api/users/admin/users/{self.standard.id}/")
        self.assertEqual(response.status_code, 403)

        self.client.force_login(self.admin)
        response = self.client.delete(f"/api/users/admin/users/{self.standard.id}/")
        self.assertEqual(response.status_code, 204)
        self.standard.refresh_from_db()
        self.assertFalse(self.standard.is_active)

    def test_only_admin_can_change_group_and_access(self):
        self.client.force_login(self.hod)
        response = self.client.patch(
            f"/api/users/admin/users/{self.standard.id}/role-access/",
            {
                "group_type": GROUP_TYPE_HEAD_OF_DEPARTMENT,
                "access_level": ACCESS_LEVEL_2,
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

        self.client.force_login(self.admin)
        response = self.client.patch(
            f"/api/users/admin/users/{self.standard.id}/role-access/",
            {
                "group_type": GROUP_TYPE_HEAD_OF_DEPARTMENT,
                "access_level": ACCESS_LEVEL_2,
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.standard.refresh_from_db()
        self.assertEqual(self.standard.profile.group_type, GROUP_TYPE_HEAD_OF_DEPARTMENT)
        self.assertEqual(self.standard.profile.access_level, ACCESS_LEVEL_2)
