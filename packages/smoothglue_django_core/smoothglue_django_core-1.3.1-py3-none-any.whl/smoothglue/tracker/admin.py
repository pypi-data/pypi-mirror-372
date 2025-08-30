from django.contrib import admin

from smoothglue.tracker.models import APIChangeLog, AppErrorLog


@admin.register(APIChangeLog)
class APIChangeLogAdmin(admin.ModelAdmin):
    search_fields = ["full_path"]
    list_display = ("full_path", "username", "method", "timestamp", "data")
    list_filter = (
        "username",
        "method",
        "timestamp",
    )
    readonly_fields = ["username", "full_path", "method", "timestamp", "data", "params"]
    ordering = ("-timestamp",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(AppErrorLog)
class AppErrorLogAdmin(admin.ModelAdmin):
    search_fields = ["user"]
    list_display = ("level", "message", "user", "timestamp")
    list_filter = (
        "user",
        "level",
        "timestamp",
    )
    readonly_fields = [
        "user",
        "level",
        "message",
        "stack_trace",
        "client_data",
        "timestamp",
    ]
    ordering = ("-timestamp",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser
