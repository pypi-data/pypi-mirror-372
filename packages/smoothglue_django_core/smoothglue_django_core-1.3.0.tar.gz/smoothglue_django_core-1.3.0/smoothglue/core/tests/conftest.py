from contextlib import contextmanager
from unittest.mock import AsyncMock, patch

import async_property
import pytest
import rest_framework
from adrf import serializers as adrf_serializers
from django.db.models import Manager, Model, TextField


@pytest.fixture(scope="session")
def get_test_model():
    class SomeModel(Model):
        name = TextField()

        async def asave(*args, **kwargs):
            return True

    return SomeModel


@pytest.fixture(scope="session")
def get_test_audit_model():
    from smoothglue.core.models import AuditModel

    class SomeAuditModel(AuditModel):
        name = TextField()

        async def asave(*args, **kwargs):
            return True

    return SomeAuditModel


@pytest.fixture
def get_test_async_serializer(get_test_model):
    SomeModel = get_test_model

    class SomeAsyncSerializer(adrf_serializers.ModelSerializer):
        @async_property.async_property
        async def adata(self):
            return {}

        def create(self, *args, **kwargs):
            return SomeModel(id=1, name="some name")

        class Meta:
            model = SomeModel
            fields = ["name"]

    return SomeAsyncSerializer


@pytest.fixture
def get_test_sync_serializer(get_test_model):
    SomeModel = get_test_model

    class SomeSyncSerializer(rest_framework.serializers.ModelSerializer):
        def data(self):
            return {}

        def create(self, *args, **kwargs):
            return SomeModel(id=1, name="some name")

        class Meta:
            model = SomeModel
            fields = ["name"]

    return SomeSyncSerializer


@pytest.fixture
def patch_db_operations():
    @contextmanager
    def patch_db_operations_context(return_value: Model):
        with (
            patch.object(
                Manager, "create", autospec=True, return_value=return_value
            ) as mock_create,
            patch.object(
                Manager,
                "acreate",
                new_callable=AsyncMock,
                return_value=return_value,
            ) as mock_acreate,
            patch.object(
                Model, "save", autospec=True, return_value=return_value
            ) as mock_save,
        ):
            yield mock_create, mock_acreate, mock_save

    return patch_db_operations_context
