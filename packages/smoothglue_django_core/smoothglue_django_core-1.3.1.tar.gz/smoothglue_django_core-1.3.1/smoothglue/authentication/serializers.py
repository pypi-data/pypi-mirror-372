from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import serializers

from smoothglue.authentication.models import (
    OrganizationCategory,
    OrganizationMember,
    PlatformOrganization,
)
from smoothglue.core.serializers.abstract import DefaultSerializer


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name"]


class OrganizationCategorySerializer(DefaultSerializer):
    class Meta:
        model = OrganizationCategory
        fields = ["id", "name", "description", "data"]


class PlatformOrganizationSerializer(DefaultSerializer):
    class Meta:
        model = PlatformOrganization
        fields = [
            "id",
            "name",
            "child_organizations",
            "group",
            "abbreviation",
            "org_category",
            "data",
        ]

    def get_fields(self):
        fields = super().get_fields()
        fields["child_organizations"] = PlatformOrganizationSerializer(
            many=True, read_only=True
        )
        return fields


# pylint: disable=W0223
class UserDataSerializer(serializers.Serializer):
    """
    Custom Serializer for JSONField data schema. This will allow the openAPI
    describe what are acceptable for the 'data' JSON format.
    """

    rank = serializers.CharField(required=False)
    usercertificate = serializers.CharField(required=False)
    affiliation = serializers.CharField(required=False)

    def to_representation(self, instance):
        return instance


class PlatformUserSerializer(DefaultSerializer):
    organizations = serializers.PrimaryKeyRelatedField(
        queryset=PlatformOrganization.objects.all(),
        required=False,
        allow_null=False,
        many=True,
    )
    groups = GroupSerializer(read_only=True, many=True)

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "data",
            "organizations",
            "groups",
            "user_image",
        ]
        extra_kwargs = {
            "organizations": {"required": False},
        }

    def update(self, instance, validated_data):
        org_ids = validated_data.pop("organizations", None)
        instance = super().update(instance, validated_data)

        if org_ids is not None:
            OrganizationMember.objects.filter(platform_user=instance).delete()
            for org in org_ids:
                OrganizationMember.objects.create(
                    platform_user=instance,
                    platform_organization=org,
                    created_by=instance,
                    updated_by=instance,
                )

        return instance

    def create(self, validated_data):
        org_ids = validated_data.pop("organizations", None)
        instance = super().create(validated_data)

        if org_ids is not None:
            for org in org_ids:
                OrganizationMember.objects.create(
                    platform_user=instance,
                    platform_organization=org,
                    created_by=instance,
                    updated_by=instance,
                )

        return instance


class SimplePlatformOrganizationSerializer(DefaultSerializer):
    class Meta:
        model = PlatformOrganization
        fields = [
            "id",
            "name",
        ]


class SimplePlatformUserSerializer(DefaultSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "email", "first_name", "last_name", "username"]


class OrganizationMemberSerializer(DefaultSerializer):

    platform_organization = SimplePlatformOrganizationSerializer()
    platform_user = SimplePlatformUserSerializer()

    class Meta:
        model = OrganizationMember
        fields = ["id", "platform_organization", "platform_user"]
