from html import unescape
from typing import Any, Dict

from django.utils.html import escape
from rest_framework import serializers

from smoothglue.core.models import AuditModel, TimeAuditModel


class DefaultSerializer(serializers.ModelSerializer):
    """
    Generic serializer to ensure all values are escaped
    """

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates and sanitizes the input data.

        This method iterates over all attributes in the input data. If an attribute
        is of type string, it escapes any HTML characters to prevent XSS attacks.
        This is particularly useful for ensuring that user input is safely
        processed and stored.

        Parameters:
        attrs (Dict[str, Any]): The input data to validate, as a dictionary
            where keys are the field names and values are the field values.

        Returns:
        Dict[str, Any]: The sanitized input data, with HTML characters in string
            fields escaped.
        """
        for key, value in attrs.items():
            if isinstance(value, str):
                attrs[key] = escape(value)
        return super().validate(attrs)

    def to_representation(self, instance):
        """
        Returned the unescaped value for str typed fields.
        """
        data = super().to_representation(instance)
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = unescape(value)
        return data

    class Meta:
        abstract = True


class TimeAuditSerializer(DefaultSerializer):
    """
    A serializer for models that include time audit fields.

    This serializer extends DefaultSerializer and is specifically designed for
    models that have 'created' and 'last_updated' fields. These fields are
    automatically set to read-only to ensure they are managed by the model itself
    and not modifiable through the serializer.

    Attributes:
        model (Model): A Django model that includes time audit fields.
        fields (list[str]): The fields to be included in the serialization.
        read_only_fields (list[str]): Fields that are read-only.
        abstract (bool): Marks the serializer as abstract.
    """

    class Meta:
        model = TimeAuditModel
        fields = ["created_at", "updated_at"]
        read_only_fields = fields
        abstract = True


class AuditSerializer(DefaultSerializer):
    """
    A serializer for models that include both time and user audit fields.

    This serializer extends DefaultSerializer and is specifically designed for
    models that, in addition to 'created' and 'last_updated' fields, also include
    'created_by' and 'updated_by' fields to track the user responsible for
    creating or updating the model instance. The user information is automatically
    extracted from the request context and applied to the model instance.

    Attributes:
        model (Model): A Django model that includes user and time audit fields.
        fields (list[str]): The fields to be included in the serialization.
        read_only_fields (list[str]): Fields that are read-only.
        abstract (bool): Marks the serializer as abstract.
    """

    class Meta:
        model = AuditModel
        fields = TimeAuditSerializer.Meta.fields + ["created_by", "updated_by"]
        read_only_fields = fields
        abstract = True

    def create(self, validated_data: Dict[str, Any]) -> Any:
        """
        Overrides the create method to add 'created_by' and 'updated_by'
        fields based on the current user before creating a new model instance.

        Parameters:
        validated_data (Dict[str, Any]): The validated data used for model instance creation.

        Returns:
        Any: The newly created model instance.
        """
        user = self.context["request"].user
        if user:
            validated_data["updated_by"] = user
            validated_data["created_by"] = user
        return super().create(validated_data)

    def update(self, instance: Any, validated_data: Dict[str, Any]) -> Any:
        """
        Overrides the update method to set the 'updated_by' field based
        on the current user before updating the model instance.

        Parameters:
        instance (Any): The model instance to update.
        validated_data (Dict[str, Any]): The validated data used for model instance updating.

        Returns:
        Any: The updated model instance.
        """
        user = self.context["request"].user
        if user:
            instance.updated_by = user
        return super().update(instance, validated_data)
