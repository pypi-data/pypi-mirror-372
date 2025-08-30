from typing import Optional, Tuple, List
from django.contrib.auth.models import Permission
from django.db import transaction

from .models import MissingPermission

# --- Permission probing utilities (from perm_probe.py) ---
DEFAULT_PERMS_MAP = {
    "GET":    ["%(app_label)s.view_%(model_name)s"],
    "OPTIONS":["%(app_label)s.view_%(model_name)s"],
    "HEAD":   ["%(app_label)s.view_%(model_name)s"],
    "POST":   ["%(app_label)s.add_%(model_name)s"],
    "PUT":    ["%(app_label)s.change_%(model_name)s"],
    "PATCH":  ["%(app_label)s.change_%(model_name)s"],
    "DELETE": ["%(app_label)s.delete_%(model_name)s"],
}


def guess_model_from_view(view) -> Optional[Tuple[str, str]]:
    model = None
    if hasattr(view, "get_queryset"):
        try:
            qs = view.get_queryset()
            if qs is not None and hasattr(qs, "model"):
                model = qs.model
        except Exception:
            pass
    if model is None and hasattr(view, "serializer_class"):
        ser = getattr(view, "serializer_class", None)
        model = getattr(getattr(ser, "Meta", None), "model", None) or model
    if model is None:
        return None
    return model._meta.app_label, model._meta.model_name


def required_perm_strings(app_label: str, model_name: str, method: str) -> List[str]:
    tpl = DEFAULT_PERMS_MAP.get(method.upper(), [])
    return [t % {"app_label": app_label, "model_name": model_name} for t in tpl]


def resolve_permissions(perm_strings: List[str]) -> List[Permission]:
    result = []
    for s in perm_strings:
        try:
            app_label, codename = s.split(".", 1)
            p = Permission.objects.select_related("content_type").get(
                content_type__app_label=app_label, codename=codename
            )
            result.append(p)
        except Exception:
            continue
    return result


# --- Recording utilities (from record.py) ---

def _dedup_append(existing: str, snippet: str, sep: str = "\n") -> str:
    snippet = (snippet or "").strip()
    if not snippet:
        return existing or ""
    existing = existing or ""
    if snippet in existing:
        return existing
    return f"{existing}{sep}{snippet}" if existing else snippet


def build_snippet(ip: str = "", url: str = "", ua: str = "", method: str = "") -> str:
    parts = []
    if ip:
        parts.append(f"ip={ip}")
    if method:
        parts.append(f"method={method}")
    if url:
        parts.append(f"url={url}")
    if ua:
        parts.append(f"ua={ua[:256]}")
    return " | ".join(parts)


@transaction.atomic
def record_missing_perm(user, permission, *, snippet: str = ""):
    obj, created = MissingPermission.objects.select_for_update().get_or_create(
        user=user,
        permission=permission,
        defaults={"note": snippet or ""},
    )
    if not created:
        obj.hits += 1
        obj.note = _dedup_append(obj.note, snippet)
    obj.save()
    return obj
