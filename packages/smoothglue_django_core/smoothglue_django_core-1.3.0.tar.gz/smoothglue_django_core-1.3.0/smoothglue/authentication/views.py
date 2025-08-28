from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from smoothglue.authentication.permissions import UserModificationPermission
from smoothglue.core.views import ListModelViewSet

from .models import (
    OrganizationCategory,
    OrganizationMember,
    PlatformOrganization,
    PlatformUser,
)
from .serializers import (
    OrganizationCategorySerializer,
    OrganizationMemberSerializer,
    PlatformOrganizationSerializer,
    PlatformUserSerializer,
)


@extend_schema(
    operation_id="authentication_active_user_retrieve",
    responses={200: PlatformUserSerializer},
    tags=["authentication"],
    description="Retrieve the active user's information.",
)
@api_view(
    ["GET"]
)  # Required for DRF Spectacular to detect function-based views in OpenAPI schema
def get_active_user(request):
    """
    Retrieve the active user's information.

    Responds with the serialized details of the authenticated user,
    or a 404 response if no matching user is found.
    """

    # Retrieve the user and serialize their data
    platform_user = get_object_or_404(PlatformUser, id=request.user.id)
    serialized_user = PlatformUserSerializer(platform_user)

    return Response(serialized_user.data, status=status.HTTP_200_OK)


class PlatformUserViewSet(ListModelViewSet):
    queryset = PlatformUser.objects.all()
    serializer_class = PlatformUserSerializer
    permission_classes = [UserModificationPermission]


@extend_schema(
    operation_id="authentication_headers_retrieve",
    responses={200: dict},
    tags=["authentication"],
    description="Retrieve request headers for debugging.",
)
@api_view(
    ["GET"]
)  # Required for DRF Spectacular to detect function-based views in OpenAPI schema
def what_are_my_headers(request):
    return Response(dict(request.headers), status=200)


class PlatformOrganizationViewSet(ListModelViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {"parent_organization": ["exact", "isnull"]}
    queryset = PlatformOrganization.objects.all()
    serializer_class = PlatformOrganizationSerializer


class OrganizationMemberViewSet(ListModelViewSet):
    filter_backends = [DjangoFilterBackend]
    queryset = OrganizationMember.objects.all()
    filterset_fields = {
        "platform_organization": ["exact", "in"],
        "platform_user": ["exact", "in"],
    }
    serializer_class = OrganizationMemberSerializer
    http_method_names = ["get", "head"]


class OrganizationCategoryViewSet(ListModelViewSet):
    filter_backends = [DjangoFilterBackend]
    queryset = OrganizationCategory.objects.all()
    serializer_class = OrganizationCategorySerializer
