import logging

from django.conf import settings
from django.db import transaction
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import exception_handler as default_exception_handler

from smoothglue.core.models import AppInfo, Classification
from smoothglue.core.serializers.app_info import AppInfoSerializer
from smoothglue.tracker.utils import create_change_log

logger = logging.getLogger(__name__)


class ListModelViewSet(viewsets.ModelViewSet):
    """
    A viewset that extends ModelViewSet to handle the creation of lists of objects.
    It includes enhanced logging for change-making operations and uses atomic
    transactions where necessary to ensure data integrity.
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
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_exception_handler(self):
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
    def create(self, request, *args, **kwargs):
        """
        Creates a single object or a list of objects. All operations are wrapped in an atomic
        transaction to ensure data integrity. A change log is created after the operation.
        """
        is_many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        create_change_log(request)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        """
        Updates an existing object. A change log is created after the operation.
        """
        response = super().update(request, *args, **kwargs)
        create_change_log(request)
        return response

    def partial_update(self, request, *args, **kwargs):
        """
        Partially updates an existing object. A change log is created after the operation.
        """
        response = super().partial_update(request, *args, **kwargs)
        create_change_log(request)
        return response

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """
        Deletes an object. The operation is wrapped in an atomic transaction to ensure
        data integrity. A change log is created after the operation.
        """
        response = super().destroy(request, *args, **kwargs)
        create_change_log(request)
        return response


class CustomDataSchema(AutoSchema):
    """
    Overrides the JSONField data field with explicit data schema
    """

    def __init__(self, **kwargs):
        self.data_schema = kwargs.pop("data_schema")
        super().__init__(**kwargs)

    def map_field(self, field):
        if field.field_name == "data":
            return self.data_schema
        return super().map_field(field)


@extend_schema(responses=AppInfoSerializer)
@api_view(http_method_names=["GET"])
def get_app_info(request):
    """
    Retrieve App Info with classification configuration for the application
    """
    classification_level = settings.CLASSIFICATION_LEVEL.lower().strip()
    info = AppInfo(
        Classification(
            level=classification_level, message=settings.CLASSIFICATION_MESSAGE
        )
    )
    return Response(AppInfoSerializer(instance=info).data)
