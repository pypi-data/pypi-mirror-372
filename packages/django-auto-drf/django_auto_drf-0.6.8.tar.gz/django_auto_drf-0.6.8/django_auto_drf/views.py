from typing import Any, Dict, List

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db.utils import OperationalError, ProgrammingError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from drf_spectacular.utils import extend_schema

from .serializers import (
    MeSerializer,
    LoginRequestSerializer,
    LoginResponseSerializer,
    LogoutResponseSerializer,
)

UserModel = get_user_model()


class MeView(APIView):
    """
    Returns the currently authenticated user's profile, including assigned groups and permissions.
    """

    permission_classes = [IsAuthenticated]

    def determine_version(self, request, *args, **kwargs):
        try:
            kwargs = {str(k): v for k, v in (kwargs or {}).items()}
        except Exception:
            kwargs = {}
        return super().determine_version(request, **kwargs)

    @extend_schema(responses=MeSerializer)
    def get(self, request, *args, **kwargs):
        # Prefetch groups to reduce queries when serializing user's groups
        try:
            user = (
                UserModel.objects.prefetch_related('groups')
                .get(pk=request.user.pk)
            )
        except Exception:
            user = request.user
        serializer = MeSerializer(user)
        return Response(serializer.data)


class LoginView(APIView):
    """
    REST login endpoint.
    Expects JSON body: {"username": "...", "password": "..."}
    Returns a DRF Token and, if available, JWT access/refresh tokens.
    """

    permission_classes = [AllowAny]

    def determine_version(self, request, *args, **kwargs):
        try:
            kwargs = {str(k): v for k, v in (kwargs or {}).items()}
        except Exception:
            kwargs = {}
        return super().determine_version(request, **kwargs)

    @extend_schema(request=LoginRequestSerializer, responses=LoginResponseSerializer)
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response({"detail": "username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        # Create a session (optional), then issue a DRF token
        login(request, user)
        response_data = {}
        # DRF Token
        try:
            token, _ = Token.objects.get_or_create(user=user)
            response_data["token"] = token.key
        except (OperationalError, ProgrammingError):
            # Token table likely missing: guide user to run migrations instead of 500 error
            response_data["token_error"] = "Token auth not initialized. Run migrations including 'rest_framework.authtoken' (python manage.py migrate)."
        # JWT via SimpleJWT (optional)
        try:
            from rest_framework_simplejwt.tokens import RefreshToken  # type: ignore

            refresh = RefreshToken.for_user(user)
            response_data["jwt"] = {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        except Exception:
            # SimpleJWT not installed or misconfigured; ignore silently but hint in response
            if "jwt" not in response_data:
                response_data["jwt_error"] = "SimpleJWT not available. Install 'djangorestframework-simplejwt' to enable JWT."
        return Response(response_data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    REST logout endpoint. Logs out the current session and revokes token if present.
    """

    permission_classes = [IsAuthenticated]

    def determine_version(self, request, *args, **kwargs):
        try:
            kwargs = {str(k): v for k, v in (kwargs or {}).items()}
        except Exception:
            kwargs = {}
        return super().determine_version(request, **kwargs)

    @extend_schema(request=None, responses=LogoutResponseSerializer)
    def post(self, request, *args, **kwargs):
        # Delete the user's token(s) to revoke access for token-auth clients
        try:
            Token.objects.filter(user=request.user).delete()
        except (OperationalError, ProgrammingError):
            # If the authtoken tables are missing, ignore token revocation.
            pass
        except Exception:
            pass
        # Also end the session if any
        logout(request)
        return Response({"detail": "Logged out"}, status=status.HTTP_200_OK)
