from smoothglue.core.serializers.dynamic import DynamicModelSerializer
from smoothglue.tracker.models import APIChangeLog, AppErrorLog


class APIChangeLogSerializer(DynamicModelSerializer):
    class Meta:
        model = APIChangeLog
        fields = [
            "id",
            "username",
            "full_path",
            "method",
            "timestamp",
            "data",
            "params",
        ]


class AppErrorLogSerializer(DynamicModelSerializer):
    def create(self, validated_data):
        """
        Auto assign the current request user as the AppErrorLog's user.
        Added request HTTP_HEADER to the client_data
        """
        request = self.context.get("request")
        if request:
            return AppErrorLog.objects.create(
                user=request.user,
                level=validated_data.get("level"),
                message=validated_data.get("message"),
                stack_trace=validated_data.get("stack_trace"),
                client_data={
                    key: request.META[key]
                    for key in request.META
                    if key.startswith("HTTP_")
                },
            )
        return AppErrorLog.objects.create(
            user=None,
            level=validated_data.get("level"),
            message=validated_data.get("message"),
            stack_trace=validated_data.get("stack_trace"),
            client_data={},
        )

    class Meta:
        model = AppErrorLog
        fields = [
            "level",
            "message",
            "stack_trace",
            "user",
            "client_data",
        ]
