from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db.models import Q
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

UserModel = get_user_model()


class GroupSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("id", "name")


class PermissionSummarySerializer(serializers.ModelSerializer):
    app_label = serializers.CharField(source="content_type.app_label")
    model = serializers.CharField(source="content_type.model")

    class Meta:
        model = Permission
        fields = ("id", "codename", "name", "app_label", "model")


class MeSerializer(serializers.ModelSerializer):
    groups = GroupSummarySerializer(many=True, read_only=True)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = UserModel
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_superuser",
            "groups",
            "permissions",
        )

    @extend_schema_field(PermissionSummarySerializer(many=True))
    def get_permissions(self, user: Any):
        qs = (
            Permission.objects.filter(Q(user=user) | Q(group__user=user))
            .select_related("content_type")
            .distinct()
            .order_by("content_type__app_label", "codename")
        )
        return PermissionSummarySerializer(qs, many=True).data


class JWTSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField(required=False)
    token_error = serializers.CharField(required=False)
    jwt = JWTSerializer(required=False)
    jwt_error = serializers.CharField(required=False)


class LogoutResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()