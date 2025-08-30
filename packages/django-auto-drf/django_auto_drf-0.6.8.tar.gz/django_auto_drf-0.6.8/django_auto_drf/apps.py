import importlib
import logging

from django.apps import AppConfig, apps

SYSTEM_APPS = ('django_auto_drf', 'rest_framework', 'drf_spectacular')


class DjangoAutoDrfAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_auto_drf'

    def ready(self):
        logger = logging.getLogger(__name__)

        # Validate AUTO_DRF_VERSIONS setting
        from django.core.exceptions import ImproperlyConfigured
        from django_auto_drf.settings import AUTO_DRF_VERSIONS
        if AUTO_DRF_VERSIONS is not None:
            if not isinstance(AUTO_DRF_VERSIONS, (list, tuple)):
                raise ImproperlyConfigured("AUTO_DRF_VERSIONS must be a list of unique, increasing integers or None")
            if len(AUTO_DRF_VERSIONS) == 0:
                raise ImproperlyConfigured("AUTO_DRF_VERSIONS cannot be an empty list; use None to disable versioning")
            # Ensure all ints
            if not all(isinstance(v, int) for v in AUTO_DRF_VERSIONS):
                raise ImproperlyConfigured("AUTO_DRF_VERSIONS must contain only integers")
            # Ensure sorted strictly increasing and unique
            sorted_versions = sorted(AUTO_DRF_VERSIONS)
            if list(AUTO_DRF_VERSIONS) != sorted_versions:
                raise ImproperlyConfigured("AUTO_DRF_VERSIONS must be sorted in increasing order")
            if len(set(AUTO_DRF_VERSIONS)) != len(AUTO_DRF_VERSIONS):
                raise ImproperlyConfigured("AUTO_DRF_VERSIONS must not contain duplicates")

        module_names = ("views", "serializers", "filters")
        for app_config in apps.get_app_configs():
            if "django." in app_config.name or app_config.name in SYSTEM_APPS:
                continue
            for module_name in module_names:
                full_module = f"{app_config.name}.{module_name}"
                try:
                    importlib.import_module(full_module)
                    logger.debug(f"[autodiscover] Importato: {full_module}")
                except ModuleNotFoundError as e:
                    if e.name == full_module:
                        # Normale, modulo non presente
                        continue
                    logger.warning(f"[autodiscover] Errore in {full_module}: {e}")
                except Exception as e:
                    logger.warning(f"[autodiscover] Errore importando {full_module}: {e}")
