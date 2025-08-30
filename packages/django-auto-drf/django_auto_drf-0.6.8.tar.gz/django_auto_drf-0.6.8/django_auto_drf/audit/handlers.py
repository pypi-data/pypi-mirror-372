from rest_framework.views import exception_handler as drf_exception_handler
from .utils import (
    guess_model_from_view,
    required_perm_strings,
    resolve_permissions,
    record_missing_perm,
    build_snippet,
)


def audit_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is None or response.status_code != 403:
        return response

    request = context.get("request")
    view = context.get("view")
    user = getattr(request, "user", None)
    if not (user and user.is_authenticated):
        return response  # ignore anonymous

    app_model = guess_model_from_view(view)
    if not app_model:
        return response

    app_label, model_name = app_model
    perm_strings = required_perm_strings(app_label, model_name, request.method)
    permissions = resolve_permissions(perm_strings)
    if not permissions:
        return response

    snippet = build_snippet(
        ip=request.META.get("REMOTE_ADDR", ""),
        url=request.build_absolute_uri() if hasattr(request, "build_absolute_uri") else request.path,
        ua=request.META.get("HTTP_USER_AGENT", ""),
        method=getattr(request, "method", ""),
    )

    for perm in permissions:
        record_missing_perm(user, perm, snippet=snippet)

    return response
