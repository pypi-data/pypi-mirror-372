from rest_framework.routers import DefaultRouter

from django_auto_drf.registry import api_registry


def api_router_urls():
    router = DefaultRouter()
    for endpoint, config in api_registry.items():
        router.register(endpoint, config.get_viewset(), config.get_base_name())
    return router.urls
