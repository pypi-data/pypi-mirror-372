from rest_framework import serializers

from smoothglue.core.models import AppInfo, Classification


class ClassificationSerializer(serializers.Serializer):
    """
    Serializer for the Classification model.
    Serializes the 'level' and 'message' fields.
    """

    level = serializers.CharField(read_only=True)
    message = serializers.CharField(read_only=True)

    def update(self, instance, validated_data):
        """
        Update and return an existing Classification instance, given the validated data.

        Args:
            instance: The existing Classification instance.
            validated_data: The validated data to update the instance with.

        Returns:
            The updated Classification instance.
        """
        instance.level = validated_data.get("level", instance.level)
        instance.message = validated_data.get("message", instance.message)
        return instance

    def create(self, validated_data):
        """
        Create and return a new Classification instance, given the validated data.

        Args:
            validated_data: The validated data to create the instance with.

        Returns:
            The newly created Classification instance.
        """
        return Classification(**validated_data)


class AppInfoSerializer(serializers.Serializer):
    """
    Serializer for the AppInfo model.
    Serializes the 'classification' field using ClassificationSerializer.
    """

    classification = ClassificationSerializer(read_only=True)

    def update(self, instance, validated_data):
        """
        Update and return an existing AppInfo instance, given the validated data.

        Args:
            instance: The existing AppInfo instance.
            validated_data: The validated data to update the instance with.

        Returns:
            The updated AppInfo instance.
        """
        instance.classification = validated_data.get(
            "classification", instance.classification
        )
        return instance

    def create(self, validated_data):
        """
        Create and return a new AppInfo instance, given the validated data.

        Args:
            validated_data: The validated data to create the instance with.

        Returns:
            The newly created AppInfo instance.
        """
        return AppInfo(**validated_data)
