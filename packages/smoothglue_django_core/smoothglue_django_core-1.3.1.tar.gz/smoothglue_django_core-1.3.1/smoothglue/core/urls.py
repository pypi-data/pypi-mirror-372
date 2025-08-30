from django.urls import include, path
from rest_framework.schemas import get_schema_view

from smoothglue.core.views import get_app_info

schema_view = get_schema_view(
    title="SmoothGlue Core",
    description="SmoothGlue Core API",
    version="1.0.0",
    patterns=[
        path("", include("smoothglue.core.urls")),
    ],
)

urlpatterns = [
    path("app_info/", get_app_info, name="app_info"),
    # path("openapi/", schema_view, name="openapi-schema"),
]
