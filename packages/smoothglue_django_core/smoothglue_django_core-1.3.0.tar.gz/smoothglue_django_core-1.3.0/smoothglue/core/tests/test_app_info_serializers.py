"""Tests for app_info serializers to improve coverage."""

import pytest

from smoothglue.core.models import AppInfo, Classification
from smoothglue.core.serializers.app_info import (
    AppInfoSerializer,
    ClassificationSerializer,
)


class TestClassificationSerializer:
    """Test ClassificationSerializer create and update methods."""

    def test_create_classification(self):
        """Test creating a new Classification instance."""
        serializer = ClassificationSerializer()
        validated_data = {"level": "unclassified", "message": "Test message"}

        classification = serializer.create(validated_data)

        assert isinstance(classification, Classification)
        assert classification.level == "unclassified"
        assert classification.message == "Test message"

    def test_update_classification(self):
        """Test updating an existing Classification instance."""
        serializer = ClassificationSerializer()
        instance = Classification(level="secret", message="Old message")
        validated_data = {"level": "unclassified", "message": "New message"}

        updated = serializer.update(instance, validated_data)

        assert updated.level == "unclassified"
        assert updated.message == "New message"

    def test_update_classification_partial(self):
        """Test partial update of Classification instance."""
        serializer = ClassificationSerializer()
        instance = Classification(level="secret", message="Old message")
        validated_data = {"level": "unclassified"}

        updated = serializer.update(instance, validated_data)

        assert updated.level == "unclassified"
        assert updated.message == "Old message"  # Should remain unchanged


class TestAppInfoSerializer:
    """Test AppInfoSerializer create and update methods."""

    def test_create_app_info(self):
        """Test creating a new AppInfo instance."""
        serializer = AppInfoSerializer()
        classification = Classification(level="unclassified", message="Test")
        validated_data = {"classification": classification}

        app_info = serializer.create(validated_data)

        assert isinstance(app_info, AppInfo)
        assert app_info.classification == classification

    def test_update_app_info(self):
        """Test updating an existing AppInfo instance."""
        serializer = AppInfoSerializer()
        old_classification = Classification(level="secret", message="Old")
        new_classification = Classification(level="unclassified", message="New")
        instance = AppInfo(classification=old_classification)
        validated_data = {"classification": new_classification}

        updated = serializer.update(instance, validated_data)

        assert updated.classification == new_classification

    def test_update_app_info_no_classification(self):
        """Test updating AppInfo without providing classification."""
        serializer = AppInfoSerializer()
        classification = Classification(level="secret", message="Original")
        instance = AppInfo(classification=classification)
        validated_data = {}

        updated = serializer.update(instance, validated_data)

        assert updated.classification == classification  # Should remain unchanged
