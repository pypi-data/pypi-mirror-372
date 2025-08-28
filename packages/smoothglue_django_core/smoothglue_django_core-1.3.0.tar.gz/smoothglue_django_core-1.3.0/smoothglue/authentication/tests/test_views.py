from unittest import mock

from django.shortcuts import reverse
from rest_framework.test import APITestCase

from smoothglue.authentication.models import PlatformOrganization, PlatformUser


class TestPlatformUser(APITestCase):
    ENDPOINT = reverse("users-list")

    def setUp(self):
        self.obj = PlatformUser.objects.create(
            username="Test",
            email="test@platform.test",
        )
        self.org = PlatformOrganization.objects.create(name="test")

    def test_get_list(self):
        resp = self.client.get(self.ENDPOINT, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp.data) > 0)

    def test_get(self):
        resp = self.client.get(f"{self.ENDPOINT}{self.obj.id}/", format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["username"], self.obj.username)

    @mock.patch(
        "smoothglue.authentication.permissions.UserModificationPermission.has_object_permission"
    )
    def test_patch(self, mockPermission):
        """
        PATCH should only update data that is passed in
        """
        mockPermission.return_value = True
        resp = self.client.patch(
            f"{self.ENDPOINT}{self.obj.id}/",
            data={
                "first_name": "Test",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["first_name"], "Test")

    @mock.patch(
        "smoothglue.authentication.permissions.UserModificationPermission.has_object_permission"
    )
    def test_put(self, mockPermission):
        """
        PUT update all data that is passed in
        """
        mockPermission.return_value = True
        resp = self.client.put(
            f"{self.ENDPOINT}{self.obj.id}/",
            data={
                "username": "TEST",
                "first_name": "John",
                "last_name": "Doe",
                "email": "test@test.com",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["username"], "TEST")
        self.assertEqual(resp.data["first_name"], "John")
        self.assertEqual(resp.data["last_name"], "Doe")

    @mock.patch(
        "smoothglue.authentication.permissions.UserModificationPermission.has_object_permission"
    )
    def test_post(self, mockPermission):
        mockPermission.return_value = True
        resp = self.client.post(
            self.ENDPOINT,
            data={
                "username": "TEST",
                "first_name": "John",
                "last_name": "Doe",
                "email": "test@test.com",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["username"], "TEST")
        self.assertEqual(resp.data["first_name"], "John")
        self.assertEqual(resp.data["last_name"], "Doe")

    @mock.patch(
        "smoothglue.authentication.permissions.UserModificationPermission.has_object_permission"
    )
    def test_delete(self, mockPermission):
        mockPermission.return_value = True
        resp = self.client.delete(f"{self.ENDPOINT}{self.obj.id}/", format="json")
        self.assertEqual(resp.status_code, 204)

    @mock.patch(
        "smoothglue.authentication.permissions.UserModificationPermission.has_object_permission"
    )
    def test_patch_nested_org(self, mockPermission):
        """
        PATCH should only update data that is passed in
        """
        mockPermission.return_value = True
        resp = self.client.patch(
            f"{self.ENDPOINT}{self.obj.id}/",
            data={"organizations": [str(self.org.id)]},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["organizations"], [self.org.id])
