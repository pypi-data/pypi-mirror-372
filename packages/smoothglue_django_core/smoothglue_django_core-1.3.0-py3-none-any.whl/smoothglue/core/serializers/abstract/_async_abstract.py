from html import unescape
from typing import Any

from adrf.serializers import ModelSerializer
from django.db.models import Model
from django.utils.html import escape

from smoothglue.core.models import AuditModel, TimeAuditModel


class AsyncDefaultSerializer(ModelSerializer):
    """
    A serializer that escapes HTML in input data and unescapes HTML in output data.
    This serializer is designed to be used with asynchronous views.
    """

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """
        Validate and escape HTML in the input data.

        Args:
            attrs (dict[str, Any]): The input data to validate.

        Returns:
            dict[str, Any]: The validated and escaped data.
        """
        for key, value in attrs.items():
            if isinstance(value, str):
                attrs[key] = escape(value)
        return super().validate(attrs)

    async def ato_representation(self, instance: Model) -> str:
        """
        Asynchronously convert the instance to its representation
        and unescape HTML in the output data.

        Args:
            instance (Model): The instance to convert.

        Returns:
            str: The unescaped representation of the instance.
        """
        data = await super().ato_representation(instance)
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = unescape(value)
        return data

    def to_representation(self, instance: Model) -> str:
        """
        Convert the instance to its representation and unescape HTML in the output data.

        Args:
            instance (Model): The instance to convert.

        Returns:
            str: The unescaped representation of the instance.
        """
        data = super().to_representation(instance)
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = unescape(value)
        return data

    class Meta:
        """
        Meta options for the serializer.
        """

        abstract = True


class AsyncTimeAuditSerializer(AsyncDefaultSerializer):
    """
    Serializer for the TimeAuditModel.
    Serializes the 'created_at' and 'updated_at' fields.
    """

    class Meta:
        """
        Meta options for the TimeAuditSerializer.
        """

        model = TimeAuditModel
        fields = ["created_at", "updated_at"]
        read_only_fields = fields
        abstract = True


class AsyncAuditSerializer(AsyncDefaultSerializer):
    """
    Serializer for the AuditModel.
    Serializes the fields from TimeAuditSerializer and adds 'created_by' and 'updated_by' fields.
    """

    class Meta:
        """
        Meta options for the AuditSerializer.
        """

        model = AuditModel
        fields = AsyncTimeAuditSerializer.Meta.fields + ["created_by", "updated_by"]
        read_only_fields = fields
        abstract = True

    async def acreate(self, validated_data: dict[str, Any]) -> Model:
        """
        Asynchronously create a new AuditModel instance,
        setting the 'created_by' and 'updated_by' fields.

        Args:
            validated_data (dict[str, Any]): The validated data to create the instance with.

        Returns:
            Model: The newly created AuditModel instance.
        """
        user = self.context["request"].user
        if user:
            validated_data["updated_by"] = user
            validated_data["created_by"] = user
        return await super().acreate(validated_data)

    async def aupdate(self, instance: Model, validated_data: dict[str, Any]) -> Model:
        """
        Asynchronously update an existing AuditModel instance, setting the 'updated_by' field.

        Args:
            instance (Model): The existing AuditModel instance.
            validated_data (dict[str, Any]): The validated data to update the instance with.

        Returns:
            Model: The updated AuditModel instance.
        """
        user = self.context["request"].user
        if user:
            instance.updated_by = user
        return await super().aupdate(instance, validated_data)
