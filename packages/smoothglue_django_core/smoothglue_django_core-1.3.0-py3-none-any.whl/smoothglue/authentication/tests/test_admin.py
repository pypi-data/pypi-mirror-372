from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models
from django.test import RequestFactory, TestCase

from smoothglue.authentication.admin import (
    OrganizationCategoryAdmin,
    OrganizationMembersInline,
    PlatformOrganizationAdmin,
    PlatformOrganizationMembersInline,
    PlatformOrganizationsInline,
    UserAdmin,
)
from smoothglue.authentication.models import OrganizationCategory, PlatformOrganization

User = get_user_model()


class MockRequest:
    pass


class TestUserAdmin(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.user_admin = UserAdmin(User, self.site)
        self.request = RequestFactory().get("/admin/authentication/user/")

    def test_readonly_fields(self):
        self.assertEqual(self.user_admin.readonly_fields, ("username", "email"))

    def test_list_display(self):
        self.assertEqual(
            self.user_admin.list_display,
            ("username", "email", "first_name", "last_name", "is_staff"),
        )

    def test_search_fields(self):
        self.assertEqual(
            self.user_admin.search_fields,
            ("username", "email", "first_name", "last_name"),
        )

    def test_list_filter(self):
        self.assertEqual(
            self.user_admin.list_filter,
            ("is_staff", "is_superuser", "is_active", "groups"),
        )

    def test_formfield_overrides(self):
        self.assertIn(models.JSONField, self.user_admin.formfield_overrides)

    def test_fieldsets(self):
        self.assertEqual(len(self.user_admin.fieldsets), 5)

    def test_inlines(self):
        self.assertIn(OrganizationMembersInline, self.user_admin.inlines)


class TestPlatformOrganizationAdmin(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.platform_org_admin = PlatformOrganizationAdmin(
            PlatformOrganization, self.site
        )
        self.request = RequestFactory().get(
            "/admin/authentication/platformorganization/"
        )

    def test_list_display(self):
        self.assertEqual(
            self.platform_org_admin.list_display,
            (
                "name",
                "parent_organization",
                "org_category",
                "abbreviation",
                "child_organizations",
            ),
        )

    def test_list_editable(self):
        self.assertEqual(
            self.platform_org_admin.list_editable,
            ("parent_organization", "org_category", "abbreviation"),
        )

    def test_inlines(self):
        self.assertIn(PlatformOrganizationsInline, self.platform_org_admin.inlines)
        self.assertIn(
            PlatformOrganizationMembersInline, self.platform_org_admin.inlines
        )


class TestOrganizationCategoryAdmin(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.org_category_admin = OrganizationCategoryAdmin(
            OrganizationCategory, self.site
        )
        self.request = RequestFactory().get(
            "/admin/authentication/organizationcategory/"
        )

    def test_list_display(self):
        self.assertEqual(self.org_category_admin.list_display, ("name", "description"))
