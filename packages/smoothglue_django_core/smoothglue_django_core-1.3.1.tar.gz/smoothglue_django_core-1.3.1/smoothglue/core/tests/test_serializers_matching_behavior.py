import asyncio
from unittest.mock import MagicMock

import pytest
from django.contrib.auth import get_user_model
from rest_framework.request import Request

from smoothglue.core.serializers.abstract import (
    AsyncAuditSerializer,
    AsyncDefaultSerializer,
    AuditSerializer,
    DefaultSerializer,
)


@pytest.mark.parametrize(
    "sync_function_name, async_function_name, args, kwargs",
    [
        ("validate", "validate", [], {"attrs": {"name": "some_name"}}),
        ("to_representation", "ato_representation", [], {"instance": "get_instance"}),
        ("to_representation", "to_representation", [], {"instance": "get_instance"}),
    ],
)
@pytest.mark.asyncio
async def test_sync_and_async_serializers_have_same_behavior(
    sync_function_name, async_function_name, args, kwargs, get_test_model
):
    """
    Given an instance of a DefaultSerializer and AsyncDefaultSerializer
    When call any given overridden function on both instances
    Then we expect the output and behavior to be the same
    """
    SomeModel = get_test_model

    if kwargs.get("instance") == "get_instance":
        kwargs["instance"] = SomeModel(pk=1, name="some_name")

    class SomeSyncDefaultSerializer(DefaultSerializer):
        class Meta:
            model = SomeModel
            fields = ["name"]

    class SomeAsyncDefaultSerializer(AsyncDefaultSerializer):
        class Meta:
            model = SomeModel
            fields = ["name"]

    some_sync_serializer = SomeSyncDefaultSerializer()
    some_async_serializer = SomeAsyncDefaultSerializer()

    sync_result = getattr(some_sync_serializer, sync_function_name)(*args, **kwargs)

    async_function = getattr(some_async_serializer, async_function_name)
    if asyncio.iscoroutinefunction(async_function):
        async_result = await async_function(*args, **kwargs)
    else:
        async_result = async_function(*args, **kwargs)

    assert sync_result == async_result


@pytest.mark.parametrize(
    "sync_function_name, async_function_name, args, kwargs",
    [
        ("create", "acreate", [], {"validated_data": {"name": "some_name"}}),
        (
            "update",
            "aupdate",
            [],
            {"instance": "get_instance", "validated_data": {"name": "some_name"}},
        ),
    ],
)
@pytest.mark.asyncio
async def test_sync_and_async_audit_serializers_have_same_behavior(
    sync_function_name,
    async_function_name,
    args,
    kwargs,
    get_test_audit_model,
    patch_db_operations,
):
    """
    Given an instance of an AuditSerializer and an AsyncAuditSerializer
    When we call the overridden functions on the serializer instances with the same inputs
    Then we expect the same outputs and behavior
    """
    # Setup
    SomeAuditModel = get_test_audit_model
    some_audit_model_instance = SomeAuditModel(name="some_name")

    if kwargs.get("instance") == "get_instance":
        kwargs["instance"] = some_audit_model_instance

    UserModel = get_user_model()

    some_user = UserModel()

    class SomeSyncAuditSerializer(AuditSerializer):
        class Meta:
            model = SomeAuditModel
            fields = AuditSerializer.Meta.fields + ["name"]

    class SomeAsyncAuditSerializer(AsyncAuditSerializer):
        class Meta:
            model = SomeAuditModel
            fields = AsyncAuditSerializer.Meta.fields + ["name"]

    mock_request = MagicMock(spec=Request)
    mock_request.user = some_user

    context = {"request": mock_request}
    some_sync_serializer = SomeSyncAuditSerializer(context=context)

    some_async_serializer = SomeAsyncAuditSerializer(context=context)

    # Test
    with patch_db_operations(return_value=some_audit_model_instance):
        sync_result = getattr(some_sync_serializer, sync_function_name)(*args, **kwargs)

        async_result = await getattr(some_async_serializer, async_function_name)(
            *args, **kwargs
        )

    assert sync_result == async_result
