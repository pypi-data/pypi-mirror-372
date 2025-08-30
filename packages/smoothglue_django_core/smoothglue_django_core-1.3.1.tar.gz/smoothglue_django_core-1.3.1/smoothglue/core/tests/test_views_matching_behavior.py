from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from adrf.mixins import UpdateModelMixin as AsyncUpdateModelMixin
from asgiref.sync import sync_to_async
from rest_framework.mixins import DestroyModelMixin, UpdateModelMixin
from rest_framework.views import Request

from smoothglue.core.views import AsyncListModelViewSet, ListModelViewSet


@pytest.mark.parametrize(
    "sync_function_name, async_function_name",
    [
        ("list", "alist"),
        ("create", "acreate"),
        ("update", "aupdate"),
        ("partial_update", "partial_aupdate"),
        ("destroy", "adestroy"),
    ],
)
@pytest.mark.asyncio
@pytest.mark.django_db
@patch.object(DestroyModelMixin, "perform_destroy")
@patch.object(UpdateModelMixin, "perform_update")
@patch.object(AsyncUpdateModelMixin, "perform_aupdate", new_callable=AsyncMock)
async def test_sync_and_async_views_have_same_behavior(
    _mock_perform_aupdate,
    _mock_perform_update,
    _mock_perform_destroy,
    sync_function_name,
    async_function_name,
    get_test_model,
    get_test_sync_serializer,
    get_test_async_serializer,
):
    """
    Given ListModelViewSet and AsyncModelViewSet instances
    When we call equivalent functions (i.e. `list` and `alist`)
    Then we expecte the same results for both function calls
    And their behavior should match exactly

    NOTE: This is a smoke test for detecting ListModelViewSet and AsyncListModelViewSet
    diverging in behavior. They should match.
    """
    # Setup
    SomeModel = get_test_model
    SomeSyncSerializer = get_test_sync_serializer
    SomeAsyncSerializer = get_test_async_serializer
    SOME_NAME = "some name"
    SOME_OBJECT = {"pk": 1, "name": SOME_NAME}

    class SomeListModelViewSet(ListModelViewSet):
        serializer_class = SomeSyncSerializer

        def get_queryset(self):
            return None

    class SomeAsyncListModelViewSet(AsyncListModelViewSet):
        serializer_class = SomeAsyncSerializer

        def get_queryset(self):
            return None

    sync_view_set = SomeListModelViewSet()
    sync_view_set.request = None
    sync_view_set.format_kwarg = None
    sync_view_set.kwargs = SOME_OBJECT

    async_view_set = SomeAsyncListModelViewSet()
    async_view_set.request = None
    async_view_set.format_kwarg = None
    async_view_set.kwargs = SOME_OBJECT

    some_model_instance = SomeModel(pk=1, name=SOME_NAME)
    mock_request = MagicMock(spec=Request)
    mock_request.data = {"id": 1, "name": SOME_NAME}
    mock_request._request = MagicMock()

    # Test
    with patch(
        "rest_framework.generics.get_object_or_404", return_value=some_model_instance
    ):
        sync_result = await sync_to_async(getattr(sync_view_set, sync_function_name))(
            mock_request
        )

    match async_function_name:
        case "adestroy":  # adestroy calls sync function under the hood
            with patch(
                "rest_framework.generics.get_object_or_404",
                return_value=some_model_instance,
            ):
                async_result = await getattr(async_view_set, async_function_name)(
                    mock_request
                )
        case _:
            with patch(
                "adrf.generics.aget_object_or_404",
                new_callable=AsyncMock,
                return_value=some_model_instance,
            ):
                async_result = await getattr(async_view_set, async_function_name)(
                    mock_request
                )

    assert sync_result.status_code == async_result.status_code

    match sync_function_name:
        # For some reason `data` is sometimes returned as a function or property
        case "create" | "update" | "partial_update":
            assert sync_result.data() == async_result.data
        case _:
            assert sync_result.data == async_result.data
