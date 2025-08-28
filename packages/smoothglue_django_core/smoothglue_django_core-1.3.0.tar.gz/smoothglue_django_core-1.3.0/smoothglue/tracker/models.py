import uuid

from django.conf import settings
from django.db import models


class APIChangeLog(models.Model):
    """
    Enables logs of API-based changes to be viewed in admin.
    Not meant to be used directly (see base.logging.py)
    Intentionally does not have UUID
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=200, blank=True)
    full_path = models.CharField(max_length=200, blank=True)
    method = models.CharField(max_length=30, blank=True)
    timestamp = models.DateTimeField(blank=True)
    data = models.JSONField(default=dict)
    params = models.JSONField(default=dict)

    def __str__(self):
        return f"{str(self.method)}: {str(self.full_path)}"

    class Meta:
        verbose_name = "API Change Log"


class AppErrorLog(models.Model):
    LOG_LEVELS = (
        ("WARNING", "Warning"),
        ("ERROR", "Error"),
        ("FATAL", "Fatal"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    level = models.CharField(max_length=10, choices=LOG_LEVELS)
    message = models.CharField(max_length=200)
    stack_trace = models.TextField(
        blank=True, null=True, help_text="Stack trace error logging if it's available"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        help_text="User data if available",
    )
    client_data = models.TextField(
        blank=True,
        null=True,
        help_text="Any other client data, user agent, ip address etc",
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "App Error Log"
