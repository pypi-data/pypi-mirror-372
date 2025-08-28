from unittest.mock import Mock, patch

from django.conf import settings
from django.test import TestCase, override_settings
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from smoothglue.authentication.models import (
    PlatformOrganization,
    is_group_security_enabled,
    post_save_user_signal_handler,
    post_save_org_signal_handler,
    post_save_org_member_signal_handler,
    post_delete_org_member_signal_handler,
)

User = get_user_model()


class UserSignalTests(TestCase):
    """Tests for signals related to the PlatformUser model."""

    def test_new_user_added_to_default_group(self):
        """
        Verify a new user is added to the default 'Participant' group if it exists.
        """
        participant_group, _ = Group.objects.get_or_create(name="Participant")
        user = User.objects.create_user(username="testuser1", email="test1@example.com")
        self.assertIn(participant_group, user.groups.all())

    @override_settings(GLOBAL_USER_GROUP_NAME="CustomGlobalGroup")
    def test_new_user_added_to_settings_group(self):
        """
        Verify a new user is added to the group specified in settings.
        """
        custom_group, _ = Group.objects.get_or_create(name="CustomGlobalGroup")
        user = User.objects.create_user(username="testuser2", email="test2@example.com")
        self.assertIn(custom_group, user.groups.all())

    def test_user_not_added_if_group_does_not_exist(self):
        """
        Verify the signal does nothing if the target group isn't in the database.
        """
        Group.objects.filter(name="Participant").delete()
        user = User.objects.create_user(username="testuser3", email="test3@example.com")
        self.assertEqual(user.groups.count(), 0)

    def test_signal_does_not_fire_on_user_update(self):
        """
        Verify the signal only runs on user creation, not on updates.
        """
        user = User.objects.create_user(username="testuser4", email="test4@example.com")
        self.assertEqual(user.groups.count(), 0)
        user.first_name = "Updated"
        user.save()
        self.assertEqual(user.groups.count(), 0)


@override_settings(ENABLE_GROUP_SECURITY=True)
class OrganizationSignalTests(TestCase):
    """
    Tests for signals related to PlatformOrganization and its members.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="orguser", email="orguser@example.com"
        )
        self.org = PlatformOrganization.objects.create(name="Test Corp")
        self.org.refresh_from_db()

    def test_org_creation_creates_linked_group(self):
        self.assertIsNotNone(self.org.group)
        self.assertEqual(self.org.group.name, self.org.name)
        self.assertTrue(Group.objects.filter(name="Test Corp").exists())

    @override_settings(ENABLE_GROUP_SECURITY=False)
    def test_org_creation_does_not_create_group_if_disabled(self):
        org_no_group = PlatformOrganization.objects.create(name="No Group Corp")
        self.assertIsNone(org_no_group.group)

    def test_adding_user_to_org_adds_to_group(self):
        self.assertNotIn(self.org.group, self.user.groups.all())
        self.org.platform_users.add(self.user)
        self.assertIn(self.org.group, self.user.groups.all())

    def test_removing_user_from_org_removes_from_group(self):
        self.org.platform_users.add(self.user)
        self.assertIn(self.org.group, self.user.groups.all())
        self.org.platform_users.remove(self.user)
        self.assertNotIn(self.org.group, self.user.groups.all())


class SignalHandlerUnitTests(TestCase):
    """
    Unit tests that call signal handler functions directly to test their
    internal logic for full coverage.
    """

    def test_is_group_security_enabled_helper(self):
        """Tests the `is_group_security_enabled` helper function."""
        with override_settings(ENABLE_GROUP_SECURITY=True):
            self.assertTrue(is_group_security_enabled())
        with override_settings(ENABLE_GROUP_SECURITY=False):
            self.assertFalse(is_group_security_enabled())
        # Test default behavior when setting is not present
        with override_settings():
            delattr(settings, "ENABLE_GROUP_SECURITY")
            self.assertFalse(is_group_security_enabled())

    @patch("smoothglue.authentication.models.Group.objects.filter")
    def test_post_save_user_handler_logic(self, mock_group_filter):
        """Unit tests the user creation signal handler."""
        mock_user = Mock(spec=User)
        mock_group = Mock(spec=Group)
        # Simulate the group existing
        mock_group_filter.return_value.first.return_value = mock_group

        post_save_user_signal_handler(instance=mock_user, created=True)
        mock_user.groups.add.assert_called_once_with(mock_group)
        mock_user.save.assert_called_once()

        mock_user.reset_mock()
        post_save_user_signal_handler(instance=mock_user, created=False)
        mock_user.groups.add.assert_not_called()

    @patch("smoothglue.authentication.models.Group.objects.create")
    @override_settings(ENABLE_GROUP_SECURITY=True)
    def test_post_save_org_handler_logic(self, mock_group_create):
        """Unit tests the organization creation signal handler."""
        mock_org = Mock(spec=PlatformOrganization, name="New Org")

        post_save_org_signal_handler(instance=mock_org, created=True)

        self.assertTrue(mock_org.save.called)

    def test_organization_member_signal_handlers(self):
        """Unit tests the handlers for OrganizationMember creation and deletion."""
        mock_user = Mock(spec=User)
        mock_group = Mock(spec=Group)
        mock_org = Mock(spec=PlatformOrganization, group=mock_group)
        mock_member = Mock(platform_user=mock_user, platform_organization=mock_org)

        with override_settings(ENABLE_GROUP_SECURITY=True):
            # Test add signal
            post_save_org_member_signal_handler(instance=mock_member, created=True)
            mock_user.groups.add.assert_called_once_with(mock_group)

            # Test delete signal
            post_delete_org_member_signal_handler(instance=mock_member)
            mock_user.groups.remove.assert_called_once_with(mock_group)
