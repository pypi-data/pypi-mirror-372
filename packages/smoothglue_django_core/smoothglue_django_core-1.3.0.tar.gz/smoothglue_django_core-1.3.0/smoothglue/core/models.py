from django.conf import settings
from django.db import models


class TimeAuditModel(models.Model):
    """Abstract class to give timestamp audit fields to other models"""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditModel(TimeAuditModel):
    """Abstract class to include user audits with timestamp audit fields"""

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)ss_created",
        blank=True,
        null=True,
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)ss_updated",
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True


class Classification:
    """
    Classification data
    """

    def __init__(self, level, message):
        self.level = level
        self.message = message


class AppInfo:
    """
    Non DB object for serializing data
    """

    def __init__(self, classification) -> None:
        self.classification = classification
