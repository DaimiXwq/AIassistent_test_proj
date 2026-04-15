from django.contrib.auth import get_user_model
from django.test import TestCase

from users.constants import (
    ACCESS_LEVEL_1,
    ACCESS_LEVEL_2,
    ACCESS_LEVEL_3,
    ACCESS_LEVEL_4,
    ACCESS_LEVEL_ADMIN,
    GROUP_TYPE_ADMIN,
    GROUP_TYPE_HEAD_OF_DEPARTMENT,
    GROUP_TYPE_STANDARD,
)

User = get_user_model()


class UserFixturesMixin:
    """Reusable deterministic fixture users across all groups and levels."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.fixture_users = {}

        cls.fixture_users["admin_admin"] = cls._create_user_with_profile(
            username="fixture_admin",
            group_type=GROUP_TYPE_ADMIN,
            access_level=ACCESS_LEVEL_ADMIN,
        )
        cls.fixture_users["hod_level_2"] = cls._create_user_with_profile(
            username="fixture_hod",
            group_type=GROUP_TYPE_HEAD_OF_DEPARTMENT,
            access_level=ACCESS_LEVEL_2,
        )

        # Standard group users for all non-admin levels.
        cls.fixture_users["standard_level_1"] = cls._create_user_with_profile(
            username="fixture_standard_l1",
            group_type=GROUP_TYPE_STANDARD,
            access_level=ACCESS_LEVEL_1,
        )
        cls.fixture_users["standard_level_2"] = cls._create_user_with_profile(
            username="fixture_standard_l2",
            group_type=GROUP_TYPE_STANDARD,
            access_level=ACCESS_LEVEL_2,
        )
        cls.fixture_users["standard_level_3"] = cls._create_user_with_profile(
            username="fixture_standard_l3",
            group_type=GROUP_TYPE_STANDARD,
            access_level=ACCESS_LEVEL_3,
        )
        cls.fixture_users["standard_level_4"] = cls._create_user_with_profile(
            username="fixture_standard_l4",
            group_type=GROUP_TYPE_STANDARD,
            access_level=ACCESS_LEVEL_4,
        )

    @classmethod
    def _create_user_with_profile(cls, username, group_type, access_level, password="StrongPass123!"):
        user = User.objects.create_user(username=username, password=password)
        user.profile.group_type = group_type
        user.profile.access_level = access_level
        user.profile.save()
        return user


class AdminUserManagementApiTests(UserFixturesMixin, TestCase):
    def setUp(self):
        self.admin = self.fixture_users["admin_admin"]
        self.hod = self.fixture_users["hod_level_2"]
        self.standard = self.fixture_users["standard_level_4"]

    def test_only_admin_and_hod_can_create_user(self):
        self.client.force_login(self.standard)
        response = self.client.post(
            "/api/users/admin/users/",
            {"username": "attempt_from_standard", "password": "StrongPass123!"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

        self.client.force_login(self.hod)
        response = self.client.post(
            "/api/users/admin/users/",
            {"username": "created_by_hod", "password": "StrongPass123!"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)

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

    def test_only_admin_can_deactivate_user(self):
        self.client.force_login(self.hod)
        response = self.client.delete(f"/api/users/admin/users/{self.standard.id}/")
        self.assertEqual(response.status_code, 403)

        self.client.force_login(self.admin)
        response = self.client.delete(f"/api/users/admin/users/{self.standard.id}/")
        self.assertEqual(response.status_code, 204)
        self.standard.refresh_from_db()
        self.assertFalse(self.standard.is_active)

    def test_only_admin_can_assign_group_and_access(self):
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

    def test_head_of_department_cannot_escalate_group_during_creation(self):
        self.client.force_login(self.hod)

        response = self.client.post(
            "/api/users/admin/users/",
            {
                "username": "hod_escalation_attempt",
                "password": "StrongPass123!",
                "group_type": GROUP_TYPE_ADMIN,
                "access_level": ACCESS_LEVEL_ADMIN,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(username="hod_escalation_attempt").exists())


class AdminUserManagementNegativeBypassTests(UserFixturesMixin, TestCase):
    def setUp(self):
        self.admin = self.fixture_users["admin_admin"]
        self.hod = self.fixture_users["hod_level_2"]
        self.target_user = self.fixture_users["standard_level_3"]

    def test_unauthenticated_direct_calls_are_blocked(self):
        create_response = self.client.post(
            "/api/users/admin/users/",
            {"username": "anonymous_create", "password": "StrongPass123!"},
            content_type="application/json",
        )
        self.assertIn(create_response.status_code, (401, 403))

        delete_response = self.client.delete(f"/api/users/admin/users/{self.target_user.id}/")
        self.assertIn(delete_response.status_code, (401, 403))

        role_response = self.client.patch(
            f"/api/users/admin/users/{self.target_user.id}/role-access/",
            {
                "group_type": GROUP_TYPE_STANDARD,
                "access_level": ACCESS_LEVEL_1,
            },
            content_type="application/json",
        )
        self.assertIn(role_response.status_code, (401, 403))

    def test_hod_cannot_bypass_checks_with_direct_admin_access_level_payload(self):
        self.client.force_login(self.hod)
        response = self.client.post(
            "/api/users/admin/users/",
            {
                "username": "hod_direct_payload_attempt",
                "password": "StrongPass123!",
                "group_type": GROUP_TYPE_STANDARD,
                "access_level": ACCESS_LEVEL_ADMIN,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(username="hod_direct_payload_attempt").exists())

    def test_even_admin_cannot_bypass_role_access_consistency_rules(self):
        self.client.force_login(self.admin)
        response = self.client.patch(
            f"/api/users/admin/users/{self.target_user.id}/role-access/",
            {
                "group_type": GROUP_TYPE_STANDARD,
                "access_level": ACCESS_LEVEL_ADMIN,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.profile.group_type, GROUP_TYPE_STANDARD)
        self.assertEqual(self.target_user.profile.access_level, ACCESS_LEVEL_3)


class AccessLevelDefaultRuleTests(UserFixturesMixin, TestCase):
    def test_base_rule_access_level_4_is_default_for_every_new_user(self):
        new_user = User.objects.create_user(username="default_level_user", password="StrongPass123!")
        self.assertEqual(new_user.profile.access_level, ACCESS_LEVEL_4)

    def test_access_level_4_is_applied_when_create_api_payload_omits_level(self):
        admin = self.fixture_users["admin_admin"]
        self.client.force_login(admin)

        response = self.client.post(
            "/api/users/admin/users/",
            {
                "username": "api_default_level_user",
                "password": "StrongPass123!",
                "group_type": GROUP_TYPE_STANDARD,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        created = User.objects.get(username="api_default_level_user")
        self.assertEqual(created.profile.access_level, ACCESS_LEVEL_4)
