from unittest.mock import patch

import jwt
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.test import TestCase
from django.test.utils import override_settings

from smoothglue.authentication.auth import (
    PlatformAuthentication,
    decode_jwt,
    get_unknown_user,
)


class TestDecodeJWT(TestCase):
    def setUp(self):
        self.request = HttpRequest()

    @patch("jwt.decode")
    def test_decode_jwt_with_authorization_header(self, mock_jwt_decode):
        mock_jwt_decode.return_value = {"some": "data"}
        self.request.META["HTTP_AUTHORIZATION"] = "Bearer testtoken"
        result = decode_jwt(self.request)
        self.assertEqual(result, {"some": "data"})
        mock_jwt_decode.assert_called_once_with(
            "testtoken", options={"verify_signature": False}
        )

    @patch("jwt.decode")
    def test_decode_jwt_with_jwt_header(self, mock_jwt_decode):
        mock_jwt_decode.return_value = {"some": "data"}
        self.request.META["HTTP_JWT"] = "testtoken"
        result = decode_jwt(self.request)
        self.assertEqual(result, {"some": "data"})
        mock_jwt_decode.assert_called_once_with(
            "testtoken", options={"verify_signature": False}
        )

    def test_decode_jwt_no_token(self):
        with self.assertRaises(ValueError) as context:
            decode_jwt(self.request)
        self.assertEqual(str(context.exception), "No JWT provided in header.")

    @patch("jwt.decode", side_effect=jwt.DecodeError("Invalid token"))
    def test_decode_jwt_invalid_token(self, mock_jwt_decode):
        self.request.META["HTTP_AUTHORIZATION"] = "Bearer invalidtoken"
        with self.assertRaises(ValueError) as context:
            decode_jwt(self.request)
        self.assertEqual(str(context.exception), "Invalid JWT token: Invalid token")


class TestGetUnknownUser(TestCase):
    @override_settings(SINGLE_USER_DEFAULT_EMAIL="default@example.com")
    def test_get_unknown_user(self):
        user = get_unknown_user()
        self.assertEqual(user.email, "default@example.com")
        self.assertEqual(user.username, "UnknownUser")
        self.assertTrue(user.is_superuser)


class TestPlatformAuthentication(TestCase):
    def setUp(self):
        self.auth = PlatformAuthentication()
        self.request = HttpRequest()

    @override_settings(ENABLE_SINGLE_USER_MODE=True)
    @patch(
        "smoothglue.authentication.auth.get_unknown_user",
        return_value={"id": 1, "name": "foo"},
    )
    def test_authenticate_single_user_mode(self, mock_get_unknown_user):
        user, _ = self.auth.authenticate(self.request)
        self.assertEqual(user, {"id": 1, "name": "foo"})

    @patch("smoothglue.authentication.auth.decode_jwt")
    @patch("django.contrib.auth.get_user_model")
    def test_authenticate_with_valid_jwt(self, mock_get_user_model, mock_decode_jwt):
        mock_decode_jwt.return_value = {
            "email": "test@example.com",
            "preferred_username": "testuser",
            "given_name": "Test",
            "family_name": "User",
            "rank": "N/A",
            "usercertificate": "N/A",
            "affiliation": "N/A",
        }
        self.request.META["HTTP_AUTHORIZATION"] = "Bearer validtoken"
        user, _ = self.auth.authenticate(self.request)
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.username, "testuser")
        self.assertFalse(user.is_superuser)

    @patch("smoothglue.authentication.auth.decode_jwt")
    def test_authenticate_with_invalid_jwt(self, mock_decode_jwt):
        mock_decode_jwt.side_effect = ValueError("Invalid JWT token")
        self.request.META["HTTP_AUTHORIZATION"] = "Bearer invalidtoken"
        with self.assertRaises(ValueError) as context:
            self.auth.authenticate(self.request)
        self.assertEqual(str(context.exception), "Invalid JWT token")

    def test_is_valid_email(self):
        self.assertTrue(self.auth.is_valid_email("valid@example.com"))

    def test_is_invalid_email(self):
        self.assertFalse(self.auth.is_valid_email("invalid"))

    @patch("django.contrib.auth.validators.UnicodeUsernameValidator")
    def test_is_valid_username(self, mock_unicode_username_validator):
        validator_instance = mock_unicode_username_validator.return_value
        self.assertTrue(self.auth.is_valid_username("validusername"))
        validator_instance.assert_called_once_with("validusername")

    @patch("django.contrib.auth.validators.UnicodeUsernameValidator")
    def test_is_invalid_username(self, mock_unicode_username_validator):
        validator_instance = mock_unicode_username_validator.return_value
        validator_instance.side_effect = ValidationError("Invalid username")
        self.assertFalse(self.auth.is_valid_username("invalidusername"))
        validator_instance.assert_called_once_with("invalidusername")
