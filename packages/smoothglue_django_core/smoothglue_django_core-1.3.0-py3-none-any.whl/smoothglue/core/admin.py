from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget


class DataAdmin(admin.ModelAdmin):
    """
    This provides an easier WYSIWYG JSON Editor for JSONField
    """

    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }


class BaseAuditModelAdmin(DataAdmin):
    """
    This base admin class will disable the audit fields and will auto populate
    the audit fields based on the request users.
    """

    readonly_fields = ("created_by", "updated_by", "created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        return super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not hasattr(instance, "created_by"):
                instance.created_by = request.user
            instance.updated_by = request.user
            instance.save()
