from django.conf import settings as django_settings

DJANGO_AUTO_DRF_DEFAULT_VIEWSET = getattr(
    django_settings,
    "DJANGO_AUTO_DRF_DEFAULT_VIEWSET",
    "rest_framework.viewsets.ModelViewSet"
)
DJANGO_AUTO_DRF_DEFAULT_SERIALIZER = getattr(
    django_settings,
    "DJANGO_AUTO_DRF_DEFAULT_SERIALIZER",
    "rest_framework.serializers.ModelSerializer"
)
DJANGO_AUTO_DRF_DEFAULT_FILTERSET = getattr(
    django_settings,
    "DJANGO_AUTO_DRF_DEFAULT_FILTERSET",
    "django_filters.rest_framework.FilterSet"
)

# Aggiunta di nuovi settings
DJANGO_AUTO_DRF_DEFAULT_BASE_URL = getattr(
    django_settings,
    "DJANGO_AUTO_DRF_DEFAULT_BASE_URL",
    "api/"
)
DJANGO_AUTO_DRF_DISABLE_SCHEMA_GENERATION = getattr(
    django_settings,
    "DJANGO_AUTO_DRF_DISABLE_SCHEMA_GENERATION",
    False
)
