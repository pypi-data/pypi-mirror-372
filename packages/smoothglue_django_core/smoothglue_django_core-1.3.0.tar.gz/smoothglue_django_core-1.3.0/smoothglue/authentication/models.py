import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.db.models.constraints import Deferrable, UniqueConstraint
from django.db.models.signals import m2m_changed
from django.dispatch.dispatcher import receiver

from smoothglue.core.models import AuditModel


class PlatformUser(AbstractUser):
    """
    Extended Django User Model that has additional
    properties that can be stored against the user
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data = models.JSONField(default=dict, blank=True)
    email = models.EmailField(unique=True)
    organizations = models.ManyToManyField(
        to="PlatformOrganization",
        default=None,
        through="OrganizationMember",
        related_name="members",
        through_fields=["platform_user", "platform_organization"],
    )
    user_image = models.ImageField(upload_to=None, null=True, blank=True)

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else str(self.username)


@receiver(models.signals.post_save, sender=get_user_model())
def post_save_user_signal_handler(instance, created, **kwargs):
    """
    Allows newly created users to be added to the global user group if the
    GLOBAL_USER_GROUP_NAME configuration is a set and the group exist in the
    database.
    """
    if created:
        global_user_group = "Participant"
        if hasattr(settings, "GLOBAL_USER_GROUP_NAME"):
            global_user_group = settings.GLOBAL_USER_GROUP_NAME
        group = Group.objects.filter(name=global_user_group).first()
        if group:
            instance.groups.add(group)
            instance.save()


class OrganizationMember(AuditModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    platform_organization = models.ForeignKey(
        "PlatformOrganization", on_delete=models.CASCADE
    )
    platform_user = models.ForeignKey(PlatformUser, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["platform_organization", "platform_user"],
                name="unique_overlap",
                deferrable=Deferrable.DEFERRED,
            ),
        ]


class OrganizationCategory(AuditModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False, blank=False, unique=True)
    description = models.TextField(null=True, blank=True)
    data = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name_plural = "Organization Categories"

    def __str__(self):
        return self.name


class PlatformOrganization(AuditModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False, blank=False, unique=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    parent_organization = models.ForeignKey(
        "PlatformOrganization",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="child_organizations",
        help_text="Parent Organization",
    )
    platform_users = models.ManyToManyField(
        to=PlatformUser,
        default=None,
        through=OrganizationMember,
        through_fields=["platform_organization", "platform_user"],
    )
    abbreviation = models.CharField(max_length=10, null=True, blank=True)
    org_category = models.ForeignKey(
        OrganizationCategory, on_delete=models.CASCADE, null=True, blank=True
    )
    data = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return self.name


def is_group_security_enabled():
    enable_group_security = False
    if hasattr(settings, "ENABLE_GROUP_SECURITY"):
        enable_group_security = settings.ENABLE_GROUP_SECURITY
    return enable_group_security


@receiver(models.signals.post_save, sender=PlatformOrganization)
def post_save_org_signal_handler(instance, created, **kwargs):
    """
    when ENABLE_GROUP_SECURITY is configured, a Django group object will be created
    anytime a new PlatformOrganization is created.
    """
    if created and is_group_security_enabled():
        group = Group.objects.create(name=instance.name)
        instance.group = group
        instance.save()


@receiver(models.signals.post_save, sender=OrganizationMember)
def post_save_org_member_signal_handler(instance, created, **kwargs):
    """
    when ENABLE_GROUP_SECURITY is configured, a Django group object will be created
    anytime a new PlatformOrganization is created.
    """
    if created and is_group_security_enabled() and instance.platform_organization.group:
        instance.platform_user.groups.add(instance.platform_organization.group)


@receiver(models.signals.post_delete, sender=OrganizationMember)
def post_delete_org_member_signal_handler(instance, **kwargs):
    """
    when ENABLE_GROUP_SECURITY is configured, delete user group membership when the user
    is taken out from the organization.
    """
    if is_group_security_enabled() and instance.platform_organization.group:
        instance.platform_user.groups.remove(instance.platform_organization.group)


@receiver(m2m_changed, sender=PlatformOrganization.platform_users.through)
def org_users_changed(sender, instance, action, pk_set=None, model=None, **kwargs):
    if isinstance(instance, PlatformOrganization):
        new_users = model.objects.filter(id__in=pk_set)
        for user in new_users:
            if action == "post_add":
                user.groups.add(instance.group)
            elif action == "post_remove":
                user.groups.remove(instance.group)
    elif isinstance(instance, PlatformUser):
        user = instance
        teams = model.objects.filter(id__in=pk_set)
        for team in teams:
            if action == "post_add":
                user.groups.add(team.group)
            elif action == "post_remove":
                user.groups.remove(team.group)
