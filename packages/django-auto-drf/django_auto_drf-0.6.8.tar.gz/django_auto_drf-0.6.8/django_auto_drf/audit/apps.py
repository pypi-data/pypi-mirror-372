from django.apps import AppConfig


class AuditConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_auto_drf.audit"
    verbose_name = "Audit – Missing Permissions"
