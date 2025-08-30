from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db import models
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from django_json_widget.widgets import JSONEditorWidget

from smoothglue.authentication.models import (
    OrganizationCategory,
    OrganizationMember,
    PlatformOrganization,
)
from smoothglue.core.admin import BaseAuditModelAdmin

User = get_user_model()


class OrganizationMembersInline(admin.TabularInline):
    model = OrganizationMember
    readonly_fields = BaseAuditModelAdmin.readonly_fields
    fk_name = "platform_user"


class UserAdmin(BaseUserAdmin):
    """
    Enhanced admin view for the User model that provides additional
    features like filtering, searching, and a custom layout for JSON fields.
    Some fields are read-only as they can only be changed in Keycloak.
    """

    readonly_fields = (
        "username",
        "email",
    )
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
    )
    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
    )
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }

    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        ("Personal info", {"fields": (("first_name", "last_name"), "user_image")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        ("Custom Data", {"fields": ("data",)}),
    )
    inlines = (OrganizationMembersInline,)


class PlatformOrganizationsInline(admin.TabularInline):
    model = PlatformOrganization
    readonly_fields = BaseAuditModelAdmin.readonly_fields + ("group",)


class PlatformOrganizationMembersInline(admin.TabularInline):
    model = OrganizationMember
    readonly_fields = BaseAuditModelAdmin.readonly_fields


class PlatformOrganizationAdmin(BaseAuditModelAdmin):
    model = PlatformOrganization
    inlines = (
        PlatformOrganizationsInline,
        PlatformOrganizationMembersInline,
    )
    list_display = (
        "name",
        "parent_organization",
        "org_category",
        "abbreviation",
        "child_organizations",
    )
    list_editable = ("parent_organization", "org_category", "abbreviation")

    def child_organizations(self, obj):
        return format_html_join(
            mark_safe("<br>"),
            "<a href='/admin/authentication/platformorganization/{}'>{}</>",
            (
                (
                    org.id,
                    org.name,
                )
                for org in obj.child_organizations.all()
            ),
        ) or mark_safe("-")

    readonly_fields = BaseAuditModelAdmin.readonly_fields + ("group",)
    classes = ["wide", "extrapretty"]


class OrganizationCategoryAdmin(BaseAuditModelAdmin):
    model = OrganizationCategory
    list_display = ("name", "description")


admin.site.register(User, UserAdmin)
admin.site.register(PlatformOrganization, PlatformOrganizationAdmin)
admin.site.register(OrganizationCategory, OrganizationCategoryAdmin)
