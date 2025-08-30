"""Tests for admin.py to improve coverage."""

from unittest.mock import MagicMock, patch

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models

from smoothglue.core.admin import BaseAuditModelAdmin

User = get_user_model()


# Test model for admin testing
class AuditTestModel(models.Model):
    """Test model with audit fields."""

    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="+", null=True
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="+", null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "core"


class AuditTestModelAdmin(BaseAuditModelAdmin):
    """Test admin class for AuditTestModel."""

    pass


@pytest.mark.django_db
class TestBaseAuditModelAdmin:
    """Test BaseAuditModelAdmin save methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.site = AdminSite()
        self.admin = AuditTestModelAdmin(AuditTestModel, self.site)
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com"
        )

    def test_save_model_create(self):
        """Test save_model method when creating new object."""
        request = MagicMock()
        request.user = self.user

        obj = AuditTestModel(name="Test Object")
        form = MagicMock()
        change = False  # Creating new object

        # Mock the parent save_model method
        with patch.object(BaseAuditModelAdmin.__bases__[0], "save_model") as mock_super:
            self.admin.save_model(request, obj, form, change)

            # Check that audit fields are set correctly
            assert obj.created_by == self.user
            assert obj.updated_by == self.user
            mock_super.assert_called_once_with(request, obj, form, change)

    def test_save_model_update(self):
        """Test save_model method when updating existing object."""
        request = MagicMock()
        request.user = self.user

        # Create another user for original created_by
        original_user = User.objects.create_user(
            username="original", email="original@example.com"
        )

        obj = AuditTestModel(name="Test Object", created_by=original_user)
        form = MagicMock()
        change = True  # Updating existing object

        # Mock the parent save_model method
        with patch.object(BaseAuditModelAdmin.__bases__[0], "save_model") as mock_super:
            self.admin.save_model(request, obj, form, change)

            # Check that only updated_by is changed, not created_by
            assert obj.created_by == original_user  # Should remain unchanged
            assert obj.updated_by == self.user
            mock_super.assert_called_once_with(request, obj, form, change)

    def test_save_formset(self):
        """Test save_formset method."""
        request = MagicMock()
        request.user = self.user
        form = MagicMock()

        # Create mock formset
        formset = MagicMock()

        # Create test instances - one without created_by, one with created_by
        new_instance = MagicMock()
        new_instance.created_by = None  # Simulate new instance
        new_instance.save = MagicMock()

        existing_instance = MagicMock()
        existing_instance.created_by = self.user  # Simulate existing instance
        existing_instance.save = MagicMock()

        # Mock hasattr to return False for new instance, True for existing
        def mock_hasattr(obj, attr):
            if attr == "created_by":
                return obj.created_by is not None
            return True

        formset.save.return_value = [new_instance, existing_instance]

        change = True

        with patch("builtins.hasattr", side_effect=mock_hasattr):
            self.admin.save_formset(request, form, formset, change)

        # Check that new instance gets created_by set
        assert new_instance.created_by == self.user
        assert new_instance.updated_by == self.user

        # Check that existing instance only gets updated_by set
        assert existing_instance.updated_by == self.user

        # Verify save was called on instances
        new_instance.save.assert_called_once()
        existing_instance.save.assert_called_once()

        # Verify formset methods were called
        formset.save.assert_called_once_with(commit=False)
