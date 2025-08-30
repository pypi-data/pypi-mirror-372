"""Tests for views/_views.py to improve coverage."""

from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings
from django.test import RequestFactory
from rest_framework import status
from rest_framework.response import Response

from smoothglue.core.views._views import (
    CustomDataSchema,
    ListModelViewSet,
    get_app_info,
)


class TestListModelViewSetExceptionHandler:
    """Test exception handling in ListModelViewSet."""

    def test_exception_handler_with_default_response(self):
        """Test exception handler when default handler returns response."""
        exc = ValueError("Test error")
        context = {"request": MagicMock()}
        context["request"].method = "POST"

        # Mock default handler to return a response
        with patch(
            "smoothglue.core.views._views.default_exception_handler"
        ) as mock_handler:
            mock_response = MagicMock()
            mock_handler.return_value = mock_response

            result = ListModelViewSet.exception_handler(exc, context)

            assert result == mock_response
            mock_handler.assert_called_once_with(exc, context)

    def test_exception_handler_with_no_default_response(self):
        """Test exception handler when default handler returns None."""
        exc = ValueError("Test error")
        context = {"request": MagicMock()}
        context["request"].method = "DELETE"

        # Mock default handler to return None
        with patch(
            "smoothglue.core.views._views.default_exception_handler"
        ) as mock_handler:
            mock_handler.return_value = None

            with patch("smoothglue.core.views._views.logger") as mock_logger:
                result = ListModelViewSet.exception_handler(exc, context)

                # Check response
                assert isinstance(result, Response)
                assert result.status_code == status.HTTP_400_BAD_REQUEST
                assert result.data == {"error": "Test error"}

                # Check logging
                mock_logger.error.assert_called_once_with(
                    "Error %s object - %s: %s",
                    "deleting",
                    "ValueError",
                    "Test error",
                    exc_info=True,
                )

    def test_exception_handler_unknown_method(self):
        """Test exception handler with unknown HTTP method."""
        exc = ValueError("Test error")
        context = {"request": MagicMock()}
        context["request"].method = "HEAD"  # Not in error_verbs

        with patch(
            "smoothglue.core.views._views.default_exception_handler", return_value=None
        ):
            with patch("smoothglue.core.views._views.logger") as mock_logger:
                result = ListModelViewSet.exception_handler(exc, context)

                # Check that empty string is used for unknown method
                mock_logger.error.assert_called_once_with(
                    "Error %s object - %s: %s",
                    "",  # Empty string for unknown method
                    "ValueError",
                    "Test error",
                    exc_info=True,
                )

    def test_get_exception_handler(self):
        """Test get_exception_handler method."""
        viewset = ListModelViewSet()
        handler = viewset.get_exception_handler()
        assert handler == viewset.exception_handler


class TestCustomDataSchema:
    """Test CustomDataSchema class."""

    def test_init_with_data_schema(self):
        """Test CustomDataSchema initialization with data_schema."""
        data_schema = {"type": "object", "properties": {}}

        schema = CustomDataSchema(data_schema=data_schema)

        assert schema.data_schema == data_schema

    def test_map_field_data_field(self):
        """Test map_field method for 'data' field."""
        data_schema = {"type": "object", "properties": {}}
        schema = CustomDataSchema(data_schema=data_schema)

        # Mock field with field_name = "data"
        field = MagicMock()
        field.field_name = "data"

        result = schema.map_field(field)

        assert result == data_schema

    def test_map_field_other_field(self):
        """Test map_field method for non-'data' field."""
        data_schema = {"type": "object", "properties": {}}
        schema = CustomDataSchema(data_schema=data_schema)

        # Mock field with different field_name
        field = MagicMock()
        field.field_name = "other_field"

        # Mock parent map_field method
        with patch.object(CustomDataSchema.__bases__[0], "map_field") as mock_super:
            mock_super.return_value = {"type": "string"}

            result = schema.map_field(field)

            assert result == {"type": "string"}
            mock_super.assert_called_once_with(field)


# Note: get_app_info tests are omitted since CLASSIFICATION_LEVEL and CLASSIFICATION_MESSAGE
# are project-level settings that should be provided by the Django project using this package,
# not by the package itself. Testing these would require mocking settings which is not
# appropriate for a reusable Django app.
