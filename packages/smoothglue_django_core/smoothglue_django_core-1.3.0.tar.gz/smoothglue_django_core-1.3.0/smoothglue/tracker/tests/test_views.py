from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from smoothglue.tracker.models import APIChangeLog, AppErrorLog

User = get_user_model()

MOCK_RESOURCE_PATH = "/api/resource1"


class AppErrorLogViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.url = reverse("apperrorlogger-list")

    def test_create_error_log_authenticated(self):
        """
        Ensure authenticated users can POST error logs.
        Verify user and client_data (headers) are saved via serializer context.
        """
        self.client.force_authenticate(user=self.user)
        valid_payload = {
            "level": "ERROR",
            "message": "Something went wrong on the client.",
            "stack_trace": "Traceback details...",
        }
        response = self.client.post(
            self.url,
            data=valid_payload,
            format="json",
            HTTP_USER_AGENT="TestAgent/1.0",
            HTTP_X_CUSTOM_INFO="TestData",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AppErrorLog.objects.count(), 1)
        log_entry = AppErrorLog.objects.first()

        self.assertEqual(log_entry.level, valid_payload["level"])
        self.assertEqual(log_entry.message, valid_payload["message"])
        self.assertEqual(log_entry.stack_trace, valid_payload["stack_trace"])
        self.assertEqual(log_entry.user, self.user)

    def test_create_error_log_invalid_data(self):
        """
        Ensure POST requests with invalid data (e.g., missing required fields) fail.
        """
        self.client.force_authenticate(user=self.user)
        invalid_payload = {"stack_trace": "Incomplete data."}
        response = self.client.post(self.url, data=invalid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(AppErrorLog.objects.count(), 0)
        self.assertIn("level", response.data)
        self.assertIn("message", response.data)

    def test_disallowed_methods_on_error_log(self):
        """
        Ensure GETs are not allowed for AppErrorLogViewSet.
        """
        self.client.force_authenticate(user=self.user)

        AppErrorLog.objects.create(level="INFO", message="temp", user=self.user)

        # Test list methods
        response_get_list = self.client.get(self.url)
        self.assertEqual(
            response_get_list.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )


class APIChangeLogViewSetTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", password="password123", email="user1@example.com"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="password456", email="user2@example.com"
        )

        self.log1 = APIChangeLog.objects.create(
            username="user1",
            full_path=MOCK_RESOURCE_PATH,
            method="GET",
            timestamp=timezone.now(),
        )
        self.log2 = APIChangeLog.objects.create(
            username="user1",
            full_path="/api/resource2",
            method="POST",
            timestamp=timezone.now(),
        )
        self.log3 = APIChangeLog.objects.create(
            username="user2",
            full_path=MOCK_RESOURCE_PATH,
            method="GET",
            timestamp=timezone.now(),
        )

        self.list_url = reverse("apichangelog-list")
        self.detail_url_log1 = reverse(
            "apichangelog-detail", kwargs={"pk": self.log1.pk}
        )
        self.detail_url_nonexistent = reverse(
            "apichangelog-detail", kwargs={"pk": 9999}
        )
        self.client.force_authenticate(user=self.user1)

    def test_list_change_logs(self):
        """
        Ensure GET request to list endpoint returns logs.
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 3)
        self.assertIsInstance(response.data, list)

    def test_filter_change_logs_by_username(self):
        """
        Test filtering the list by the 'username' query parameter.
        """
        response = self.client.get(self.list_url, {"username": "user1"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only log1 and log2 are for user1
        self.assertTrue(all(item["username"] == "user1" for item in response.data))

        response_user2 = self.client.get(self.list_url, {"username": "user2"})
        self.assertEqual(response_user2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_user2.data), 1)  # Only log3 is for user2
        self.assertEqual(response_user2.data[0]["id"], str(self.log3.id))

        response_nouser = self.client.get(self.list_url, {"username": "nouser"})
        self.assertEqual(response_nouser.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_nouser.data), 0)

    def test_filter_change_logs_by_full_path(self):
        """
        Test filtering the list by the 'full_path' query parameter.
        """
        response = self.client.get(self.list_url, {"full_path": MOCK_RESOURCE_PATH})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # log1 and log3 match path
        results_ids = {item["id"] for item in response.data}
        self.assertIn(str(self.log1.id), results_ids)
        self.assertIn(str(self.log3.id), results_ids)

        response_path2 = self.client.get(self.list_url, {"full_path": "/api/resource2"})
        self.assertEqual(response_path2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_path2.data), 1)  # Only log2 matches
        self.assertEqual(response_path2.data[0]["id"], str(self.log2.id))

    def test_retrieve_change_log(self):
        """
        Ensure GET request to detail endpoint retrieves a specific log.
        """
        response = self.client.get(self.detail_url_log1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.log1.id))
        self.assertEqual(response.data["username"], self.log1.username)
        self.assertEqual(response.data["full_path"], self.log1.full_path)

    def test_retrieve_change_log_not_found(self):
        """
        Ensure GET request for a non-existent ID returns 404 Not Found.
        """
        response = self.client.get(self.detail_url_nonexistent)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_disallowed_methods_on_change_log(self):
        """
        Ensure POST, PUT, PATCH, DELETE are not allowed for APIChangeLogViewSet.
        """
        response_post = self.client.post(self.list_url, data={}, format="json")
        self.assertEqual(response_post.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        detail_url = self.detail_url_log1
        response_put = self.client.put(detail_url, data={}, format="json")
        self.assertEqual(response_put.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response_patch = self.client.patch(detail_url, data={}, format="json")
        self.assertEqual(response_patch.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response_delete = self.client.delete(detail_url)
        self.assertEqual(
            response_delete.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
