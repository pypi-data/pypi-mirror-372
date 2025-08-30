import logging

from adrf import viewsets
from adrf.mixins import get_data
from django.db.models.base import sync_to_async
from django.db.models.query import transaction
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as default_exception_handler

from smoothglue.tracker.utils import create_change_log

logger = logging.getLogger(__name__)


class AsyncListModelViewSet(
    viewsets.ModelViewSet
):  # pylint: disable=too-many-ancestors
    """
    Thin wrapper around the smoothglue.views.ListModelViewSet
    to provide async functionality through the standard View functions.
    """

    @extend_schema(
        methods=["get"],
        parameters=[
            OpenApiParameter(
                name="fields",
                type={"type": "array", "items": {"type": "string"}},
                location=OpenApiParameter.QUERY,
                description="Fields to include in the response",
            ),
        ],
    )
    async def alist(self, *args, **kwargs):
        return await super().alist(*args, **kwargs)

    def get_exception_handler(
        self,
    ):
        return self.exception_handler

    @staticmethod
    def exception_handler(exc, context):
        response = default_exception_handler(exc, context)
        if response is not None:
            return response

        error_verbs = {
            "DELETE": "deleting",
            "PUT": "modifying",
            "PATCH": "modifying",
            "POST": "creating",
        }
        logger.error(
            "Error %s object - %s: %s",
            error_verbs.get(context["request"].method, ""),
            type(exc).__name__,
            str(exc),
            exc_info=True,
        )
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def perform_create_atomic(self, serializer):
        self.perform_create(serializer)

    async def acreate(self, request, *args, **kwargs):
        """
        Creates a single object or a list of objects. All operations are wrapped in an atomic
        transaction to ensure data integrity. A change log is created after the operation.
        """
        is_many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=is_many)
        await sync_to_async(serializer.is_valid)(raise_exception=True)
        await sync_to_async(self.perform_create_atomic)(serializer)
        create_change_log(request)
        data = await get_data(serializer)
        headers = self.get_success_headers(data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    async def aupdate(self, request, *args, **kwargs):
        response = await super().aupdate(request, *args, **kwargs)
        create_change_log(request)
        return response

    async def partial_aupdate(self, request, *args, **kwargs):
        response = await super().partial_aupdate(request, *args, **kwargs)
        create_change_log(request)
        return response

    @transaction.atomic
    def destroy_atomic(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    async def adestroy(self, request, *args, **kwargs):
        response = await sync_to_async(self.destroy_atomic)(request, *args, **kwargs)
        create_change_log(request)
        return response
