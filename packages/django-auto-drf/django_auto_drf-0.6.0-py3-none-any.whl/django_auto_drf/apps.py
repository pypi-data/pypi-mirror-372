import importlib
import logging

from django.apps import AppConfig, apps

SYSTEM_APPS = ('django_auto_drf', 'rest_framework', 'drf_spectacular')


class DjangoAutoDrfAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_auto_drf'

    def ready(self):
        logger = logging.getLogger(__name__)

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
