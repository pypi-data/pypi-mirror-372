from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from smoothglue.tracker.models import APIChangeLog, AppErrorLog
from smoothglue.tracker.serializers import APIChangeLogSerializer, AppErrorLogSerializer

User = get_user_model()

FAKE_STACK_TRACE = "Trace..."


class APIChangeLogSerializerTest(TestCase):
    def setUp(self):
        self.user_obj = User.objects.create_user(
            username="testlogger", password="password123"
        )
        self.log_timestamp = timezone.now()
        self.api_log_instance = APIChangeLog.objects.create(
            username=self.user_obj.username,
            full_path="/api/test/endpoint",
            method="GET",
            timestamp=self.log_timestamp,
            data={"request_data": "sample"},
            params={"query_param": "value"},
        )

    def test_api_change_log_serialization(self):
        """
        Test that APIChangeLogSerializer correctly serializes an APIChangeLog instance.
        """
        serializer = APIChangeLogSerializer(instance=self.api_log_instance)
        data = serializer.data

        self.assertEqual(data["id"], str(self.api_log_instance.id))
        self.assertEqual(data["username"], self.api_log_instance.username)
        self.assertEqual(data["full_path"], "/api/test/endpoint")
        self.assertEqual(data["method"], "GET")
        self.assertEqual(data["data"], {"request_data": "sample"})
        self.assertEqual(data["params"], {"query_param": "value"})
        # checking that timestamp is in data due to potential
        # microsecond differences related to instantiation and test run
        self.assertTrue("timestamp" in data)
        self.assertEqual(
            data["timestamp"], self.log_timestamp.isoformat().replace("+00:00", "Z")
        )

        expected_keys = {
            "id",
            "username",
            "full_path",
            "method",
            "timestamp",
            "data",
            "params",
        }
        self.assertEqual(set(data.keys()), expected_keys)

    def test_api_change_log_deserialization_validation(self):
        """
        Test basic validation for APIChangeLogSerializer during deserialization.
        """
        valid_data = {
            "username": "newuser",
            "full_path": "/api/v2/resource",
            "method": "POST",
            "timestamp": timezone.now().isoformat(),
            "data": {"key": "payload"},
            "params": {"filter": "active"},
        }
        serializer = APIChangeLogSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())


class AppErrorLogSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="errorreporter", password="password123"
        )
        self.app_error_instance = AppErrorLog.objects.create(
            user=self.user,
            level="ERROR",
            message="Initial error for serialization test.",
            stack_trace="Traceback...",
            client_data={"HTTP_USER_AGENT": "TestClient"},
        )
        # Mock request object for context
        self.mock_request = MagicMock()
        self.mock_request.user = self.user
        self.mock_request.META = {
            "HTTP_USER_AGENT": "Chrome (Test)",
            "HTTP_X_CUSTOM_HEADER": "CustomValue",
            "CONTENT_TYPE": "application/json",  # Should not be included in client_data
            "REMOTE_ADDR": "foo",  # Should not be included
        }
        self.serializer_context = {"request": self.mock_request}

    def test_app_error_log_serialization(self):
        """
        Test that AppErrorLogSerializer correctly serializes an AppErrorLog instance.
        """
        serializer = AppErrorLogSerializer(instance=self.app_error_instance)
        data = serializer.data

        self.assertEqual(data["level"], "ERROR")
        self.assertEqual(data["message"], "Initial error for serialization test.")
        self.assertEqual(data["stack_trace"], "Traceback...")
        self.assertEqual(data["user"], self.user.pk)
        self.assertEqual(data["client_data"], "{'HTTP_USER_AGENT': 'TestClient'}")

        expected_keys = {"level", "message", "stack_trace", "user", "client_data"}
        self.assertEqual(set(data.keys()), expected_keys)

    def test_app_error_log_create_with_request_context(self):
        """
        Test the create method of AppErrorLogSerializer with a request in context.
        """
        valid_data = {
            "level": "WARNING",
            "message": "A new warning occurred.",
            "stack_trace": "Detailed traceback here.",
        }
        serializer = AppErrorLogSerializer(
            data=valid_data, context=self.serializer_context
        )
        self.assertTrue(serializer.is_valid())

    def test_app_error_log_create_without_request_context(self):
        """
        Test create method when 'request' is not in the serializer context.
        """
        valid_data = {
            "level": "ERROR",
            "message": "Informational message.",
            "stack_trace": FAKE_STACK_TRACE,
        }
        # No 'request' in context
        serializer = AppErrorLogSerializer(data=valid_data, context={})
        self.assertTrue(serializer.is_valid())

        instance = serializer.save()
        self.assertEqual(instance.level, "ERROR")
        self.assertEqual(instance.message, "Informational message.")
        self.assertEqual(instance.stack_trace, FAKE_STACK_TRACE)
        self.assertEqual(instance.client_data, {})
        self.assertIsNone(instance.user)

    def test_app_error_log_create_with_anonymous_user(self):
        """
        Test create method when request.user is None.
        """
        self.mock_request.user = (
            None  # Simulate AnonymousUser or request.user being None
        )
        valid_data = {
            "level": "DEBUG",
            "message": "Debug message from anonymous.",
            "stack_trace": FAKE_STACK_TRACE,
        }
        serializer = AppErrorLogSerializer(
            data=valid_data, context=self.serializer_context
        )
        self.assertTrue(serializer.is_valid())

        with patch(
            "smoothglue.tracker.models.AppErrorLog.objects.create"
        ) as mock_db_create:
            created_log_mock = MagicMock(
                spec=AppErrorLog, user=None
            )  # Simulate instance with user=None
            mock_db_create.return_value = created_log_mock

            instance = serializer.save()

            mock_db_create.assert_called_once()
            call_args = mock_db_create.call_args[1]
            self.assertIsNone(call_args["user"])
            self.assertEqual(instance, created_log_mock)

    def test_app_error_log_create_with_no_http_headers(self):
        """
        Test client_data is an empty dict.
        """
        self.mock_request.META = {"CONTENT_TYPE": "text/plain"}  # No HTTP headers
        valid_data = {
            "level": "CRITICAL",
            "message": "Critical issue, no headers.",
            "stack_trace": "Critical trace.",
        }
        serializer = AppErrorLogSerializer(
            data=valid_data, context=self.serializer_context
        )
        self.assertTrue(serializer.is_valid())

        with patch(
            "smoothglue.tracker.models.AppErrorLog.objects.create"
        ) as mock_db_create:
            created_log_mock = MagicMock(spec=AppErrorLog, client_data={})
            mock_db_create.return_value = created_log_mock

            serializer.save()
            call_args = mock_db_create.call_args[1]
            self.assertEqual(call_args["client_data"], {})
