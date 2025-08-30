# tests/test_admin.py (or your preferred test file location)

import unittest
from unittest.mock import Mock

# Assuming your admin.py is in 'smoothglue.tracker.admin'
# and models are in 'smoothglue.tracker.models'
# Adjust these imports based on your actual project structure.
from smoothglue.tracker.admin import APIChangeLogAdmin, AppErrorLogAdmin
from smoothglue.tracker.models import APIChangeLog, AppErrorLog

# Mock the admin site
mock_admin_site = Mock()


class APIChangeLogAdminTests(unittest.TestCase):
    def setUp(self):
        self.admin_instance = APIChangeLogAdmin(
            model=APIChangeLog, admin_site=mock_admin_site
        )
        self.mock_request_superuser = Mock()
        self.mock_request_superuser.user = Mock()
        self.mock_request_superuser.user.is_superuser = True

        self.mock_request_non_superuser = Mock()
        self.mock_request_non_superuser.user = Mock()
        self.mock_request_non_superuser.user.is_superuser = False

        self.mock_object = Mock(spec=APIChangeLog)  # A mock model instance

    def test_attributes_set_correctly(self):
        self.assertEqual(self.admin_instance.search_fields, ["full_path"])
        self.assertEqual(
            self.admin_instance.list_display,
            ("full_path", "username", "method", "timestamp", "data"),
        )
        self.assertEqual(
            self.admin_instance.list_filter, ("username", "method", "timestamp")
        )
        self.assertEqual(
            self.admin_instance.readonly_fields,
            ["username", "full_path", "method", "timestamp", "data", "params"],
        )
        self.assertEqual(self.admin_instance.ordering, ("-timestamp",))

    def test_has_add_permission(self):
        self.assertFalse(
            self.admin_instance.has_add_permission(self.mock_request_superuser)
        )
        self.assertFalse(
            self.admin_instance.has_add_permission(self.mock_request_non_superuser)
        )

    def test_has_change_permission(self):
        self.assertFalse(
            self.admin_instance.has_change_permission(self.mock_request_superuser)
        )
        self.assertFalse(
            self.admin_instance.has_change_permission(
                self.mock_request_superuser, obj=self.mock_object
            )
        )
        self.assertFalse(
            self.admin_instance.has_change_permission(self.mock_request_non_superuser)
        )
        self.assertFalse(
            self.admin_instance.has_change_permission(
                self.mock_request_non_superuser, obj=self.mock_object
            )
        )

    def test_has_view_permission_superuser(self):
        self.assertTrue(
            self.admin_instance.has_view_permission(self.mock_request_superuser)
        )
        self.assertTrue(
            self.admin_instance.has_view_permission(
                self.mock_request_superuser, obj=self.mock_object
            )
        )

    def test_has_view_permission_non_superuser(self):
        self.assertFalse(
            self.admin_instance.has_view_permission(self.mock_request_non_superuser)
        )
        self.assertFalse(
            self.admin_instance.has_view_permission(
                self.mock_request_non_superuser, obj=self.mock_object
            )
        )


class AppErrorLogAdminTests(unittest.TestCase):
    def setUp(self):
        self.admin_instance = AppErrorLogAdmin(
            model=AppErrorLog, admin_site=mock_admin_site
        )
        self.mock_request_superuser = Mock()
        self.mock_request_superuser.user = Mock()
        self.mock_request_superuser.user.is_superuser = True

        self.mock_request_non_superuser = Mock()
        self.mock_request_non_superuser.user = Mock()
        self.mock_request_non_superuser.user.is_superuser = False

        self.mock_object = Mock(spec=AppErrorLog)  # A mock model instance

    def test_attributes_set_correctly(self):
        self.assertEqual(self.admin_instance.search_fields, ["user"])
        self.assertEqual(
            self.admin_instance.list_display, ("level", "message", "user", "timestamp")
        )
        self.assertEqual(
            self.admin_instance.list_filter, ("user", "level", "timestamp")
        )
        self.assertEqual(
            self.admin_instance.readonly_fields,
            ["user", "level", "message", "stack_trace", "client_data", "timestamp"],
        )
        self.assertEqual(self.admin_instance.ordering, ("-timestamp",))

    def test_has_add_permission(self):
        self.assertFalse(
            self.admin_instance.has_add_permission(self.mock_request_superuser)
        )
        self.assertFalse(
            self.admin_instance.has_add_permission(self.mock_request_non_superuser)
        )

    def test_has_change_permission(self):
        self.assertFalse(
            self.admin_instance.has_change_permission(self.mock_request_superuser)
        )
        self.assertFalse(
            self.admin_instance.has_change_permission(
                self.mock_request_superuser, obj=self.mock_object
            )
        )
        self.assertFalse(
            self.admin_instance.has_change_permission(self.mock_request_non_superuser)
        )
        self.assertFalse(
            self.admin_instance.has_change_permission(
                self.mock_request_non_superuser, obj=self.mock_object
            )
        )

    def test_has_view_permission_superuser(self):
        self.assertTrue(
            self.admin_instance.has_view_permission(self.mock_request_superuser)
        )
        self.assertTrue(
            self.admin_instance.has_view_permission(
                self.mock_request_superuser, obj=self.mock_object
            )
        )

    def test_has_view_permission_non_superuser(self):
        self.assertFalse(
            self.admin_instance.has_view_permission(self.mock_request_non_superuser)
        )
        self.assertFalse(
            self.admin_instance.has_view_permission(
                self.mock_request_non_superuser, obj=self.mock_object
            )
        )
