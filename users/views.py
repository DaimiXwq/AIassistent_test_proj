from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.constants import GROUP_TYPE_STANDARD
from users.permissions import is_admin_user, is_head_of_department_user
from users.serializers import UserCreateSerializer, UserRoleUpdateSerializer

User = get_user_model()


class AdminUserCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        actor = request.user
        if not (is_admin_user(actor) or is_head_of_department_user(actor)):
            return Response(
                {"error": "Создавать пользователей могут только роли admin и head_of_department."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = UserCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        if is_head_of_department_user(actor) and serializer.validated_data["group_type"] != GROUP_TYPE_STANDARD:
            return Response(
                {"error": "Роль head_of_department может создавать только пользователей группы standard."},
                status=status.HTTP_403_FORBIDDEN,
            )

        with transaction.atomic():
            user = User.objects.create_user(
                username=serializer.validated_data["username"],
                email=serializer.validated_data.get("email", ""),
                password=serializer.validated_data.get("password"),
                is_active=serializer.validated_data.get("is_active", True),
            )
            profile = user.profile
            profile.group_type = serializer.validated_data["group_type"]
            profile.access_level = serializer.validated_data["access_level"]
            profile.save()

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "group_type": user.profile.group_type,
                "access_level": user.profile.access_level,
            },
            status=status.HTTP_201_CREATED,
        )


class AdminUserDeactivateView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        actor = request.user
        if not is_admin_user(actor):
            return Response(
                {"error": "Деактивировать пользователей может только роль admin."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user = User.objects.filter(id=user_id).first()
        if user is None:
            return Response({"error": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

        user.is_active = False
        user.save(update_fields=["is_active"])

        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminUserRoleUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, user_id):
        actor = request.user
        if not is_admin_user(actor):
            return Response(
                {"error": "Изменять группу и уровень доступа может только роль admin."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user = User.objects.filter(id=user_id).first()
        if user is None:
            return Response({"error": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserRoleUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = user.profile
        profile.group_type = serializer.validated_data["group_type"]
        profile.access_level = serializer.validated_data["access_level"]
        profile.save()

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "group_type": profile.group_type,
                "access_level": profile.access_level,
            },
            status=status.HTTP_200_OK,
        )
