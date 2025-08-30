import logging

from rest_framework.exceptions import (
    AuthenticationFailed, NotAuthenticated, PermissionDenied
)
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def drf_exception_handler_logger(exc, context):
    request = context.get("request")
    user = getattr(request, 'user', None)
    ip = get_client_ip(request)
    method = request.method
    path = request.get_full_path()

    # Log di accessi non autorizzati
    if isinstance(exc, (AuthenticationFailed, NotAuthenticated, PermissionDenied)):
        if user and user.is_authenticated:
            user_info = f"user={user.username} (id={user.id})"
        else:
            user_info = "utente non autenticato"

        logger.warning(
            f"[{exc.__class__.__name__}] {user_info} - {method} {path} da IP={ip} - payload={safe_data(request.data)}"
        )

    return drf_exception_handler(exc, context)


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")


def safe_data(data):
    if not hasattr(data, 'copy'):
        return {}
    data = data.copy()
    for key in ['password', 'token', 'access', 'refresh']:
        if key in data:
            data[key] = '***'
    return dict(data)
