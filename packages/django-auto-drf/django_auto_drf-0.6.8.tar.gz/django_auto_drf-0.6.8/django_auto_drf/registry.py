from importlib import import_module

from django.core.exceptions import ImproperlyConfigured
from django_filters.rest_framework import FilterSet
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet

from django_auto_drf.core import EndpointConfig
from django_auto_drf.versioning import VersionedEndpoint
from django_auto_drf.settings import AUTO_DRF_VERSIONS

# Single internal endpoints version store
api_registry_endpoints = dict()


def _ensure_versioned_endpoint(endpoint_path: str) -> VersionedEndpoint:
    if endpoint_path not in api_registry_endpoints:
        api_registry_endpoints[endpoint_path] = VersionedEndpoint(endpoint_path)
    return api_registry_endpoints[endpoint_path]


def api_register_model(model, endpoint=None, **kwargs):
    """
    Decorator for automatic registration of ViewSets, Serializers, and FilterSets.
    Supports versioning via kwargs: version (required when ON) and last_version (optional).
    """
    model_name = model.__name__.lower()
    app_label = model._meta.app_label
    endpoint_path = endpoint or f"{app_label}/{model_name}"
    ve = _ensure_versioned_endpoint(endpoint_path)

    # Extract version metadata
    version = kwargs.pop("version", None)
    last_version = kwargs.pop("last_version", None)

    # If version not specified, choose default: first AUTO_DRF_VERSIONS or 1 when None
    if version is None:
        version = (AUTO_DRF_VERSIONS[0] if AUTO_DRF_VERSIONS else 1)

    # Create config and add to VersionedEndpoint (validations inside)
    cfg = EndpointConfig(endpoint_path, model._meta.label, version=version, last_version=last_version)
    ve.add(cfg)

    # No separate proxy registry; config is tracked in versioned store only

    # Apply remaining kwargs to config
    for key, value in kwargs.items():
        if hasattr(cfg, key):
            setattr(cfg, key, value)
        else:
            raise AttributeError(f"EndpointConfig {app_label} has no attribute {key}")

    def decorator(cls=None):
        if cls is None:
            return cfg

        # Update the appropriate fields on the current config
        if issubclass(cls, ModelViewSet):
            cfg.viewset_class = cls
        elif issubclass(cls, ModelSerializer):
            cfg.serializer_class = cls
        elif issubclass(cls, FilterSet):
            cfg.filterset_class = cls
        return cls

    return decorator


def api_register_action(model, endpoint=None, detail=True, methods=None, version: int | None = None):
    if methods is None:
        methods = ['get']
    model_name = model.__name__.lower()
    app_label = model._meta.app_label
    endpoint_path = endpoint or f"{app_label}/{model_name}"
    # Ensure endpoint exists and use the current config
    ve = _ensure_versioned_endpoint(endpoint_path)
    # Try to pick an existing config from versioned store
    cfg = ve.segments[0] if ve.segments else None
    if cfg is None:
        # If endpoint not yet registered, create a minimal config only if it does not already exist in the versioned store.
        # Otherwise, do nothing to avoid overwriting an existing endpoint defined elsewhere.
        if endpoint_path not in api_registry_endpoints or not ve.segments:
            effective_version = version if version is not None else (AUTO_DRF_VERSIONS[0] if AUTO_DRF_VERSIONS else 1)
            cfg = EndpointConfig(endpoint_path, model._meta.label, version=effective_version)
            # This add will fail if a segment with same version already exists. That's desired (do not overwrite).
            ve.add(cfg)
        else:
            # Use the first available config as representative, do not create/overwrite anything
            cfg = ve.segments[0]

    def decorator(func):
        cfg.add_action(func.__name__, func, detail=detail, methods=methods)
        return func

    return decorator


def get_endpoint_config(model, endpoint=None):
    model_name = model.__name__.lower()
    app_label = model._meta.app_label
    endpoint_path = endpoint or f"{app_label}/{model_name}"
    # Return the first segment config if present (unversioned representative)
    ve = _ensure_versioned_endpoint(endpoint_path)
    return ve.segments[0] if ve.segments else None


def load_class_from_module(module_path, class_name):
    """
    Tenta di caricare una classe specifica da un modulo dato.
    Se il modulo o la classe non esistono, restituisce None.

    :param module_path: Percorso del modulo (es. 'myapp.serializers')
    :param class_name: Nome della classe da importare (es. 'DefaultModelSerializer')
    :return: La classe se trovata, altrimenti None
    """
    try:
        module = import_module(module_path)
        return getattr(module, class_name, None)
    except (ModuleNotFoundError, ImproperlyConfigured, AttributeError):
        return None


def get_versioned_registry():
    """Return the internal map endpoint->VersionedEndpoint."""
    return api_registry_endpoints
