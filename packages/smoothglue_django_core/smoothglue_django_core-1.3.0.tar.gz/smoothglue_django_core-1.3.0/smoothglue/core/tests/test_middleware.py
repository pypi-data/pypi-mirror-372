from django.test import RequestFactory, TestCase, override_settings
from django.http import HttpResponse
from django.urls import path
from smoothglue.authentication.models import PlatformUser
from smoothglue.core.middleware import (
    DoNotTrackMiddleware,
)


def dummy_view(request):
    return HttpResponse(status=200)


urlpatterns = [
    path("test/", dummy_view),
]


@override_settings(
    INSTALLED_APPS=[
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "smoothglue.core",
        "smoothglue.authentication",
    ],
    REMOTE_USER_HEADER="HTTP_X_USERNAME",
    AUTHENTICATION_BACKENDS=["django.contrib.auth.backends.RemoteUserBackend"],
    MIDDLEWARE=[
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "smoothglue.core.middleware.CACMiddleware",
    ],
    ROOT_URLCONF="smoothglue.core.tests.test_middleware",
)
class CACMiddlewareTest(TestCase):
    def setUp(self):
        self.user = PlatformUser.objects.create(username="testuser")

    def test_user_is_authenticated_with_valid_header(self):
        response = self.client.get("/test/", HTTP_X_USERNAME="testuser")
        self.assertEqual(response.wsgi_request.user, self.user)

    def test_user_is_anonymous_with_no_header(self):
        response = self.client.get("/test/")
        self.assertTrue(response.wsgi_request.user.is_anonymous)


class DoNotTrackMiddlewareTest(TestCase):
    """Tests for the DoNotTrackMiddleware."""

    def setUp(self):
        """Set up the request factory."""
        self.factory = RequestFactory()

    def test_dnt_header_enabled(self):
        """Tests that request.DNT is True when the DNT header is '1'."""
        request = self.factory.get("/", HTTP_DNT="1")
        DoNotTrackMiddleware.process_request(request)
        self.assertTrue(request.DNT)

    def test_dnt_header_disabled(self):
        """Tests that request.DNT is False when the DNT header is '0'."""
        request = self.factory.get("/", HTTP_DNT="0")
        DoNotTrackMiddleware.process_request(request)
        self.assertFalse(request.DNT)

    def test_dnt_header_absent(self):
        """Tests that request.DNT is False when the DNT header is not present."""
        request = self.factory.get("/")
        DoNotTrackMiddleware.process_request(request)
        self.assertFalse(request.DNT)

    def test_vary_header_is_added_to_response(self):
        """Tests that 'DNT' is added to the 'Vary' header of the response."""
        request = self.factory.get("/")
        response = HttpResponse()

        processed_response = DoNotTrackMiddleware.process_response(request, response)

        self.assertEqual(processed_response.get("Vary"), "DNT")
