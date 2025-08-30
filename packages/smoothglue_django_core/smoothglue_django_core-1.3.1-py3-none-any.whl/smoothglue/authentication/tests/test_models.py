from django.conf import settings
from django.test import TestCase

from smoothglue.authentication.models import (
    OrganizationMember,
    PlatformOrganization,
    PlatformUser,
)


class TestPlatformOrganization(TestCase):
    def test_create_org_should_create_group(self):
        settings.ENABLE_GROUP_SECURITY = True
        name = "Org1"
        PlatformOrganization.objects.create(
            name=name,
        )
        obj = PlatformOrganization.objects.first()
        self.assertTrue(obj.pk)
        self.assertEqual(name, obj.name)
        self.assertIsNotNone(obj.group)

    def test_create_org_should_not_create_group_when_enable_group_security_is_false(
        self,
    ):
        settings.ENABLE_GROUP_SECURITY = False
        name = "Org1"
        PlatformOrganization.objects.create(
            name=name,
        )
        obj = PlatformOrganization.objects.first()
        self.assertTrue(obj.pk)
        self.assertEqual(name, obj.name)
        self.assertIsNone(obj.group)

    def test_user_org_member_should_have_group_membership(self):
        settings.ENABLE_GROUP_SECURITY = True
        name = "Org1"
        PlatformOrganization.objects.create(
            name=name,
        )
        obj = PlatformOrganization.objects.first()
        self.assertTrue(obj.pk)
        self.assertEqual(name, obj.name)
        self.assertIsNotNone(obj.group)

        user = PlatformUser.objects.create(username="userA")
        obj.platform_users.add(user)

        self.assertTrue(user.groups.contains(obj.group))

        obj.platform_users.remove(user)

        self.assertFalse(user.groups.contains(obj.group))

    def test_user_org_member_create_should_add_group_membership(self):
        settings.ENABLE_GROUP_SECURITY = True
        name = "Org1"
        org = PlatformOrganization.objects.create(
            name=name,
        )
        user = PlatformUser.objects.create(username="userA")

        OrganizationMember.objects.create(platform_user=user, platform_organization=org)

        user = PlatformUser.objects.filter(username="userA").first()

        self.assertTrue(len(user.groups.all()), 1)
