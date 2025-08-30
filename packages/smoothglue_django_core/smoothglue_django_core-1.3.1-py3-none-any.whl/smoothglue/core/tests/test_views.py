from unittest.mock import MagicMock, patch

import pytest
from rest_framework.views import Request

from smoothglue.core.views import AsyncListModelViewSet, ListModelViewSet


class ChildListModelViewSet(ListModelViewSet):
    function_called: bool = False

    def get_queryset(self):
        return None

    def get_serializer_class(self):
        return MagicMock()

    def list(self, request, *args, **kwargs):
        self.function_called = True
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        self.function_called = True
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.function_called = True
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self.function_called = True
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.function_called = True
        return super().destroy(request, *args, **kwargs)


class SubChildListModelViewSet(ChildListModelViewSet):
    def get_queryset(self):
        return None

    def get_serializer_class(self):
        return MagicMock()

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


@pytest.mark.parametrize(
    "calling_function_name, patch_target",
    [
        (
            "list",
            "rest_framework.viewsets.ModelViewSet.list",
        ),
        (
            "create",
            "rest_framework.viewsets.ModelViewSet.perform_create",
        ),
        (
            "update",
            "rest_framework.viewsets.ModelViewSet.update",
        ),
        (
            "partial_update",
            "rest_framework.viewsets.ModelViewSet.partial_update",
        ),
        (
            "destroy",
            "rest_framework.viewsets.ModelViewSet.destroy",
        ),
    ],
)
@pytest.mark.django_db
def test_child_function_call(calling_function_name, patch_target):
    """
    Given a class that inherits multiple times from ListModelViewSet
    When we can any of the core `view` methods
    Then overridden functions between the child and parent should still be called
    """

    sub_child_view = SubChildListModelViewSet()
    sub_child_view.request = None
    sub_child_view.format_kwarg = None
    assert sub_child_view.function_called is False

    mock_request = MagicMock()

    with patch(patch_target) as mock_list_func:
        getattr(sub_child_view, calling_function_name)(mock_request)
        mock_list_func.assert_called()
        assert sub_child_view.function_called


@pytest.mark.parametrize(
    "calling_function_name, patch_target",
    [
        (
            "alist",
            "adrf.viewsets.ModelViewSet.alist",
        ),
        (
            "acreate",
            "adrf.viewsets.ModelViewSet.perform_create",
        ),
        (
            "aupdate",
            "adrf.viewsets.ModelViewSet.aupdate",
        ),
        (
            "partial_aupdate",
            "adrf.viewsets.ModelViewSet.partial_aupdate",
        ),
        (
            "adestroy",
            "adrf.viewsets.ModelViewSet.destroy",
        ),
    ],
)
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_async_views_functions_called(
    calling_function_name, patch_target, get_test_model, get_test_async_serializer
):
    """
    Given a class that inherits multiple times from AsyncListModelViewSet
    When we can any of the core `view` methods
    Then overridden functions between the child and parent should still be called
    """
    SomeModel = get_test_model
    SomeSerializer = get_test_async_serializer

    class AsyncChildListModelViewSet(AsyncListModelViewSet):
        function_called: bool = False

        async def get_queryset(self):
            return None

        async def alist(self, request, *args, **kwargs):
            self.function_called = True
            return await super().alist(request, *args, **kwargs)

        async def acreate(self, request, *args, **kwargs):
            self.function_called = True
            return await super().acreate(request, *args, **kwargs)

        async def aupdate(self, request, *args, **kwargs):
            self.function_called = True
            return await super().aupdate(request, *args, **kwargs)

        async def partial_aupdate(self, request, *args, **kwargs):
            self.function_called = True
            return await super().partial_aupdate(request, *args, **kwargs)

        async def adestroy(self, request, *args, **kwargs):
            self.function_called = True
            return await super().adestroy(request, *args, **kwargs)

    class AsyncSubChildListModelViewSet(AsyncChildListModelViewSet):
        serializer_class = SomeSerializer

        def get_queryset(self):
            return None

        async def alist(self, request, *args, **kwargs):
            return await super().alist(request, *args, **kwargs)

        async def acreate(self, request, *args, **kwargs):
            return await super().acreate(request, *args, **kwargs)

        async def aupdate(self, request, *args, **kwargs):
            return await super().aupdate(request, *args, **kwargs)

        async def partial_aupdate(self, request, *args, **kwargs):
            return await super().partial_aupdate(request, *args, **kwargs)

        async def adestroy(self, request, *args, **kwargs):
            return await super().adestroy(request, *args, **kwargs)

        def get_exception_handler(self):
            return super().get_exception_handler()

    async_sub_child_view = AsyncSubChildListModelViewSet()
    async_sub_child_view.request = None
    async_sub_child_view.format_kwarg = None
    async_sub_child_view.kwargs = {"pk": 1}
    assert async_sub_child_view.function_called is False

    mock_request = MagicMock(spec=Request)
    mock_request.data = {"id": 1, "name": "some name"}

    with patch(
        "rest_framework.generics.get_object_or_404",
        return_value=SomeModel(pk=1, name="some name"),
    ):
        with patch(patch_target) as mock_func:
            await getattr(async_sub_child_view, calling_function_name)(mock_request)
    mock_func.assert_called()
    assert async_sub_child_view.function_called is True
