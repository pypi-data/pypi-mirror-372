
from django.conf import settings
from django.db import models
from django.contrib.auth.models import Permission

class MissingPermission(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="missing_perms"
    )
    permission = models.ForeignKey(
        Permission, on_delete=models.CASCADE, related_name="missing_by_users"
    )

    hits = models.PositiveIntegerField(default=1)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    # Nota deduplicata (IP/URL/UA, ecc.)
    note = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "permission"], name="uniq_user_permission"
            )
        ]
        ordering = ["-last_seen"]

    def __str__(self):
        return f"{self.user} missing {self.permission.content_type.app_label}.{self.permission.codename}"
