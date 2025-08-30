from collections import OrderedDict

from django.apps import apps
from django.utils.module_loading import import_string
from drf_spectacular.openapi import AutoSchema
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from django_auto_drf.settings import DJANGO_AUTO_DRF_DEFAULT_FILTERSET, DJANGO_AUTO_DRF_DEFAULT_SERIALIZER, \
    DJANGO_AUTO_DRF_DEFAULT_VIEWSET


class EndpointConfig:
    def __init__(self, endpoint, model, version=None, last_version=None):
        self._endpoint = endpoint
        self.model_label = model
        self.viewset_class = None
        self.serializer_class = None
        self.filterset_class = None
        self.permissions = None
        self.paginate_by = None
        self.extra_actions = []
        # Version metadata (used when versioning ON)
        self.version = version
        self.last_version = last_version

    def get_model_object(self):
        return apps.get_model(self.model_label)

    def get_base_name(self):
        return self._endpoint.replace("/", "-")

    def get_class_base_name(self):
        names = self._endpoint.split("/")
        return "".join(map(lambda x: x.capitalize(), names))

    def get_viewset(self):
        default_viewset_class = import_string(DJANGO_AUTO_DRF_DEFAULT_VIEWSET)
        default_serializer_class = import_string(DJANGO_AUTO_DRF_DEFAULT_SERIALIZER)
        default_filterset_class = import_string(DJANGO_AUTO_DRF_DEFAULT_FILTERSET)

        # Configura il serializer se non è definito
        model_obj = self.get_model_object()
        if not self.serializer_class:
            class AutoSerializer(default_serializer_class):
                class Meta:
                    model = model_obj
                    fields = '__all__'

            AutoSerializer.__name__ = f"Auto{self.get_class_base_name()}V{self.version}Serializer"
            self.serializer_class = AutoSerializer

        # Configura il filterset se non è definito
        if not self.filterset_class:
            class AutoFilterSet(default_filterset_class):
                class Meta:
                    model = model_obj
                    fields = '__all__'

            AutoFilterSet.__name__ = f"Auto{self.get_class_base_name()}V{self.version}Filterset"
            self.filterset_class = AutoFilterSet

        # Configura il viewset se non è definito
        if not self.viewset_class:
            # Create generated ViewSet and include optional header mixin for version visibility
            try:
                from django_auto_drf.versioning import VersionHeaderMixin
                bases = (VersionHeaderMixin, default_viewset_class)
            except Exception:
                bases = (default_viewset_class,)

            AutoViewSet = type(
                f"Auto{self.get_class_base_name()}V{self.version}ViewSet",
                bases,
                {
                    'queryset': model_obj.objects.all(),
                    'FIXED_API_VERSION': str(self.version) if self.version is not None else None,
                }
            )
            default_viewset_class = AutoViewSet
        else:
            default_viewset_class = self.viewset_class
            # Ensure fixed version attribute exists for custom viewsets too
            try:
                if getattr(default_viewset_class, 'FIXED_API_VERSION', None) is None and self.version is not None:
                    setattr(default_viewset_class, 'FIXED_API_VERSION', str(self.version))
            except Exception:
                pass

        default_viewset_class.schema = AutoSchema()
        if not getattr(default_viewset_class, "serializer_class", None):
            default_viewset_class.serializer_class = self.serializer_class
        if not getattr(default_viewset_class, "filterset_class", None):
            default_viewset_class.filterset_class = self.filterset_class
        if not getattr(default_viewset_class, "permission_classes", None) or self.permissions:
            default_viewset_class.permission_classes = self.permissions
        if (not getattr(default_viewset_class, "pagination_class", None)) and self.paginate_by:
            default_viewset_class.pagination_class = StandardResultsSetPaginationBuilder(self.paginate_by)

        for name, method in self.extra_actions:
            setattr(default_viewset_class, name, method)

        return default_viewset_class

    def add_action(self, name, func, detail=True, methods=None):
        if methods is None:
            methods = ['get']
        from rest_framework.decorators import action

        method = action(detail=detail, methods=methods)(func)
        method.__name__ = name
        self.extra_actions.append((name, method))

    def __repr__(self):
        return (
            f"APIRegistryEntry(endpoint={self._endpoint}, basename={self.get_base_name()}, model={self.model_label}, "
            f"viewset={self.viewset_class}, serializer={self.serializer_class}, filterset={self.filterset_class}, "
            f"permissions={self.permissions}, paginate_by={self.paginate_by}, version={self.version}, last_version={self.last_version})"
        )


def StandardResultsSetPaginationBuilder(paginate_by):
    class StandardResultsSetPagination(PageNumberPagination):
        page_size = paginate_by
        page_size_query_param = 'page_size'
        max_page_size = 100000

        def get_page_size(self, request):
            page_size = super().get_page_size(request)
            return page_size

        def get_paginated_response(self, data):
            return Response(OrderedDict([
                ('count', self.page.paginator.count),
                ('page', self.page.number),
                ('page_size', self.get_page_size(self.request)),
                ('results', data)
            ]))

    return StandardResultsSetPagination
