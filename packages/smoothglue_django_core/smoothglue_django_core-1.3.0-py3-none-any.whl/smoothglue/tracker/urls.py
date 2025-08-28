from django.urls import include, path
from rest_framework import routers
from rest_framework.schemas import get_schema_view

from smoothglue.tracker.views import APIChangeLogViewSet, AppErrorLogViewSet

ROUTER = routers.DefaultRouter()

ROUTER.register(r"apilog", APIChangeLogViewSet, basename="apichangelog")
ROUTER.register(r"errorlogger", AppErrorLogViewSet, basename="apperrorlogger")

schema_view = get_schema_view(
    title="SmoothGlue Tracker",
    description="SmoothGlue Tracker API",
    version="1.0.0",
    patterns=[
        path("", include("smoothglue.tracker.urls")),
    ],
)

urlpatterns = [
    path("", include(ROUTER.urls)),
]
