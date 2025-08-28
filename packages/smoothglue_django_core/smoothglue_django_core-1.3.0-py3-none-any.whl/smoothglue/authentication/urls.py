from django.urls import include, path
from rest_framework import routers

from .views import (
    OrganizationCategoryViewSet,
    OrganizationMemberViewSet,
    PlatformOrganizationViewSet,
    PlatformUserViewSet,
    get_active_user,
    what_are_my_headers,
)

# Router setup
ROUTER = routers.DefaultRouter()
ROUTER.register(r"users", PlatformUserViewSet, basename="users")
ROUTER.register(r"organizations", PlatformOrganizationViewSet)
ROUTER.register(r"org-members", OrganizationMemberViewSet)
ROUTER.register(r"org-categories", OrganizationCategoryViewSet)

# URL Patterns
urlpatterns = [
    path("active_user/", get_active_user, name="get_active_user"),
    path("headers/", what_are_my_headers, name="what_are_my_headers"),
    path("", include(ROUTER.urls)),
]
