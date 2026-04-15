from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from users.constants import (
    ACCESS_LEVEL_ADMIN,
    ACCESS_LEVEL_CHOICES,
    DEFAULT_ACCESS_LEVEL,
    DEFAULT_GROUP_TYPE,
    GROUP_TYPE_ADMIN,
    GROUP_TYPE_CHOICES,
    GROUP_TYPE_STANDARD,
)
from users.permissions import is_admin_user

User = get_user_model()


class UserCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)
    group_type = serializers.ChoiceField(choices=[choice[0] for choice in GROUP_TYPE_CHOICES], required=False)
    access_level = serializers.ChoiceField(
        choices=[choice[0] for choice in ACCESS_LEVEL_CHOICES],
        required=False,
    )
    is_active = serializers.BooleanField(required=False, default=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("User with this username already exists.")
        return value

    def validate(self, attrs):
        request = self.context["request"]
        actor = request.user
        actor_is_admin = is_admin_user(actor)

        group_type = attrs.get("group_type", DEFAULT_GROUP_TYPE)
        access_level = attrs.get("access_level", DEFAULT_ACCESS_LEVEL)

        if group_type == GROUP_TYPE_ADMIN and access_level != ACCESS_LEVEL_ADMIN:
            raise serializers.ValidationError(
                {"access_level": "Admin group type requires admin access level."}
            )
        if group_type != GROUP_TYPE_ADMIN and access_level == ACCESS_LEVEL_ADMIN:
            raise serializers.ValidationError(
                {"access_level": "Only admin group type can have admin access level."}
            )

        if not actor_is_admin:
            if group_type != GROUP_TYPE_STANDARD:
                raise serializers.ValidationError(
                    {
                        "group_type": "Only admin can assign non-standard group type during user creation."
                    }
                )
            if access_level == ACCESS_LEVEL_ADMIN:
                raise serializers.ValidationError(
                    {"access_level": "Only admin can assign admin access level."}
                )

        password = attrs.get("password")
        if password:
            validate_password(password)

        attrs["group_type"] = group_type
        attrs["access_level"] = access_level
        return attrs


class UserRoleUpdateSerializer(serializers.Serializer):
    group_type = serializers.ChoiceField(choices=[choice[0] for choice in GROUP_TYPE_CHOICES])
    access_level = serializers.ChoiceField(choices=[choice[0] for choice in ACCESS_LEVEL_CHOICES])

    def validate(self, attrs):
        group_type = attrs["group_type"]
        access_level = attrs["access_level"]

        if group_type == GROUP_TYPE_ADMIN and access_level != ACCESS_LEVEL_ADMIN:
            raise serializers.ValidationError(
                {"access_level": "Admin group type requires admin access level."}
            )
        if group_type != GROUP_TYPE_ADMIN and access_level == ACCESS_LEVEL_ADMIN:
            raise serializers.ValidationError(
                {"access_level": "Only admin group type can have admin access level."}
            )

        return attrs
