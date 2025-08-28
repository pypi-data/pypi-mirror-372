from django.conf import settings
from django.contrib.auth.middleware import PersistentRemoteUserMiddleware
from django.utils.cache import patch_vary_headers
from django.utils.deprecation import MiddlewareMixin


# pylint: disable=R0205
class DoNotTrackMiddleware(MiddlewareMixin):
    @classmethod
    def process_request(cls, request):
        """
        Sets flag request.DNT based on DNT HTTP header.
        """
        if "HTTP_DNT" in request.META and request.META["HTTP_DNT"] == "1":
            request.DNT = True
        else:
            request.DNT = False

    @classmethod
    def process_response(cls, request, response):
        """
        Adds a "Vary" header for DNT, useful for caching.
        """
        patch_vary_headers(response, ["DNT"])

        return response


class CACMiddleware(PersistentRemoteUserMiddleware):
    """
    Middleware that takes in the Authorization header to be used for
    authentication
    """

    def __init__(self, get_response):
        super().__init__(get_response)
        self.header = settings.REMOTE_USER_HEADER
