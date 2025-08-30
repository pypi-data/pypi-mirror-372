import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.pagination import LimitOffsetPagination

from smoothglue.tracker.models import APIChangeLog
from smoothglue.tracker.serializers import APIChangeLogSerializer, AppErrorLogSerializer

logger = logging.getLogger(__name__)


class AppErrorLogViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    This provides the client a last resort for notifying the backend that an exception happened.
    This silents all exceptions to ensure that the client side request doesn't fail when calling
    the fail safe endpoint.

    Only POST is allowed as viewing the exception data should be done within Django Admin

    """

    serializer_class = AppErrorLogSerializer


class APIChangeLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API for retrieving API execution logs
    """

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["username", "full_path"]
    queryset = APIChangeLog.objects.all()
    serializer_class = APIChangeLogSerializer
    pagination_class = LimitOffsetPagination
