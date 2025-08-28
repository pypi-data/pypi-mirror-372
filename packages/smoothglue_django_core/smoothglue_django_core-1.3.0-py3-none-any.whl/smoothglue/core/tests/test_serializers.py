from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from adrf.serializers import BaseSerializer
from django.db.models.manager import Manager
from rest_framework.request import Request

from smoothglue.core.serializers.abstract import (
    AsyncAuditSerializer,
    AsyncDefaultSerializer,
)
from smoothglue.core.views import AsyncListModelViewSet


@pytest.mark.parametrize(
    "serializer_class", [AsyncDefaultSerializer, AsyncAuditSerializer]
)
@pytest.mark.parametrize(
    "calling_function_name, patch_target, new_callable",
    [
        (
            "acreate",
            "adrf.serializers.ModelSerializer.validate",
            None,
        ),
        (
            "acreate",
            "adrf.serializers.ModelSerializer.validate",
            None,
        ),
        (
            "acreate",
            "adrf.serializers.ModelSerializer.ato_representation",
            AsyncMock,
        ),
        (
            "alist",
            "adrf.serializers.ModelSerializer.ato_representation",
            AsyncMock,
        ),
        (
            "aupdate",
            "adrf.serializers.ModelSerializer.validate",
            None,
        ),
        (
            "aupdate",
            "adrf.serializers.ModelSerializer.ato_representation",
            AsyncMock,
        ),
        (
            "partial_aupdate",
            "adrf.serializers.ModelSerializer.validate",
            None,
        ),
        (
            "partial_aupdate",
            "adrf.serializers.ModelSerializer.ato_representation",
            AsyncMock,
        ),
    ],
)
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_async_serializer_functions_called(
    serializer_class, calling_function_name, patch_target, new_callable, get_test_model
):
    """
    Given a serializer that is used by an async view
    When we can call any of the overridden functions
    Then we expect the top level function to also be called
    """
    # Setup
    SomeModel = get_test_model

    class AsyncSomeSerializer(serializer_class):
        class Meta:
            model = SomeModel
            fields = ["name"]

    class AsyncSomeModelViewSet(AsyncListModelViewSet):
        serializer_class = AsyncSomeSerializer

        def get_queryset(self):
            return {SomeModel(pk=1, name="some_name")}

    mock_request = MagicMock(spec=Request)
    mock_request.data = {"pk": 1, "name": "some_name"}
    mock_request._request = MagicMock()
    mock_request._request.path = "path"
    mock_request._request.method = "method"
    mock_request.query_params.dict.return_value = {}

    async_view = AsyncSomeModelViewSet()
    async_view.request = mock_request
    async_view.format_kwarg = None
    async_view.kwargs = {"pk": 1}

    some_model_instance = SomeModel(pk=1, name="some_name")
    # Mocking away access to database layer
    with (
        patch(
            "adrf.generics.aget_object_or_404",
            new_callable=AsyncMock,
            return_value=some_model_instance,
        ),
        patch(
            "rest_framework.generics.get_object_or_404",
            return_value=some_model_instance,
        ),
        patch.object(
            BaseSerializer,
            "acreate",
            new_callable=AsyncMock,
            return_value=some_model_instance,
        ),
        patch.object(
            Manager,
            "create",
            return_value=some_model_instance,
        ),
    ):
        # Test
        with patch(
            patch_target, new_callable=new_callable, return_value={"name": "some_name"}
        ) as mock_func:
            assert async_view.view_is_async
            await getattr(async_view, calling_function_name)(mock_request, partial=True)
            mock_func.assert_called()
