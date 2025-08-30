from rest_framework.routers import DefaultRouter

from django_auto_drf.registry import get_versioned_registry
from django_auto_drf.settings import AUTO_DRF_VERSIONS


def api_router_urls(version: int | None = None):
    """
    Build router URLs. When version is None and versioning is OFF, returns unversioned endpoints.
    When versioning is ON, version must be provided and endpoints are filtered per version.
    """
    router = DefaultRouter()
    reg = get_versioned_registry()
    if AUTO_DRF_VERSIONS is None:
        # versioning OFF: mount all endpoints once
        for endpoint, ve in reg.items():
            cfg = ve.get_for_version(0)  # returns single segment if exists
            if cfg is None:
                continue
            router.register(endpoint, cfg.get_viewset(), cfg.get_base_name())
        return router.urls

    # Versioning ON
    if version is None:
        raise ValueError("version is required when AUTO_DRF_VERSIONS is enabled")
    for endpoint, ve in reg.items():
        cfg = ve.get_for_version(version)
        if cfg is None:
            continue
        basename = f"{cfg.get_base_name()}-v{version}"
        router.register(endpoint, cfg.get_viewset(), basename)
    return router.urls
