import logging
from typing import Dict, Type, TypedDict

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from rest_framework import exceptions, serializers

from smoothglue.core.field_trie import ModifiedTrie
from smoothglue.core.utils import check_kwargs

logger = logging.getLogger(__name__)


class NestedFieldTypes(TypedDict):
    serializer: Type[serializers.BaseSerializer]
    model: Type[models.Model]


class DynamicModelSerializer(serializers.ModelSerializer):
    """
    A serializer base class that allows removing fields from the response
    payload via the `fields` parameter in the query string.
    """

    # Limit number of fields if they are provided
    def __init__(self, *args, **kwargs):
        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        # Not every serializer has a request associated
        if "request" in self.context:
            fields = self.context["request"].query_params.get("fields")
            if fields:
                trie = ModifiedTrie()
                requested_fields = fields.split(",")
                for rf in requested_fields:
                    trie.insert(rf)
                trie.filter_requested_fields(self.fields)

    def validate(self, attrs):
        request = self.context.get("request")
        if (
            self.instance is None
            and "id" in attrs
            and (self.partial or (request and request.method == "PATCH"))
        ):
            self.instance = self.Meta.model.objects.get(id=attrs["id"])
        return super().validate(attrs)

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        return instance


class NestedObjectModelSerializer(DynamicModelSerializer):
    """
    Serializer base class that facilitates HTTP methods POST, PUT, and PATCH for objects
    nested inside a parent's serializer.

    i.e.
        `Asset` -> use `DynamicModelSerializer`,
        `Position` (child of `Asset`)  -> use `NestedObjectModelSerializer`

        # parent serializer class
        class AssetSerializer(DynamicModelSerializer):
            positions = PositionNestedSerializer(...)  # <- nested child here
            ...

            # nested config
            parent_id_field = "asset_id"  # <- tells nested children what to look for
            # lets parent serializer methods find paths to all create/updates
            nested_field_config = {
                "positions": {"serializer": PositionSerializer, "model": Position},
                ...
            }
            ...

        # technically this acts as a parent class with the functionality to also be nested
        class PositionSerializer(NestedObjectModelSerializer):
            asset_id = serializers.PrimaryKeyRelatedField(
                            source="asset",
                            queryset=Asset.objects.all()
                        )
            ...

        # the child/nested version of the above "parent" class version
        class PositionNestedSerializer(PositionSerializer):
            # parent id `asset_id` NOT required to allow for object creation/assignment
            asset_id = serializers.PrimaryKeyRelatedField(
                source="asset", queryset=Asset.objects.all(), required=False
            )
    """

    parent_id_field = None
    nested_field_config = {}

    def __init__(self, instance=None, data=serializers.empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.nested_field_config = self.get_nested_field_config()
        self.parent_id_field = self.get_parent_id_field()

    def get_source_field_name(self, field_name: str):
        # pylint: disable=E1101
        source_field_name = self._declared_fields.get(field_name).source
        if not source_field_name:
            source_field_name = field_name
        return source_field_name

    def get_parent_id_field(self):
        assert self.parent_id_field is not None, (
            "'NestedObjectModelSerializer' should either include a `parent_id_field` "
            "attribute, or override the `get_parent_id_field()` method."
        )
        return self.parent_id_field

    def get_nested_field_config(self):
        """
        Get a `nested_field_config` which should have the following structure:
            nested_field_config = {
                "<field_name>": {
                    "serializer": <ModelSerializer>,
                    "model": <Model>,
                    "partial": <bool>
                },
                ...
            }

        Example:
            nested_field_config = {
                "positions": {"serializer": PositionSerializer, "model": Position},
            }
        """
        assert self.nested_field_config != {}, (
            "'NestedObjectModelSerializer' should either include a `nested_field_config` "
            "attribute, or override the `get_nested_field_config()` method."
        )
        return self.nested_field_config

    # pylint: disable=E1101
    def create(self, validated_data):
        obj_data = self.get_obj_data(self.nested_field_config, validated_data)
        parent_obj = self.Meta.model.objects.create(**validated_data)
        # Create/Update nested objects
        for field, d in self.nested_field_config.items():
            partial = d.get("partial", self.partial)
            self.iterate_nested_data(
                obj_data=obj_data,
                parent_instance=parent_obj,
                model=d["model"],
                field=field,
                serializer=d["serializer"],
                method="create",
                partial=partial,
            )

        return parent_obj

    def update(self, instance, validated_data):
        obj_data = self.get_obj_data(self.nested_field_config, validated_data)
        # Update/Create nested objects
        for field, d in self.nested_field_config.items():
            model = d["model"]
            source_field_name = self.get_source_field_name(field)
            many_to_many = instance._meta.get_field(source_field_name).many_to_many
            one_to_one = instance._meta.get_field(source_field_name).one_to_one
            partial = d.get("partial", self.partial)
            updated_ids = self.iterate_nested_data(
                obj_data=obj_data,
                parent_instance=instance,
                model=d["model"],
                field=field,
                serializer=d["serializer"],
                method="update",
                partial=partial,
            )
            # In case of PUT, clean up removed references
            if not partial and not many_to_many and not one_to_one:
                to_delete_objects = (
                    model.objects.filter(**{self.parent_id_field: instance.id})
                    .exclude(pk__in=updated_ids)
                    .all()
                )
                for obj in to_delete_objects:
                    obj.delete()

        return super().update(instance, validated_data)

    def iterate_nested_data(self, **kwargs):
        # Check args and unpack
        check_kwargs(
            ["obj_data", "parent_instance", "model", "field", "serializer", "method"],
            kwargs,
        )
        obj_data = kwargs["obj_data"]
        parent_instance = kwargs["parent_instance"]
        field = kwargs["field"]
        method = kwargs["method"]
        partial = kwargs["partial"]
        assert method in ["update", "create"]

        updated_ids = []
        source_field_name = self.get_source_field_name(field)
        many_to_many = parent_instance._meta.get_field(source_field_name).many_to_many
        if field in obj_data:
            for data in obj_data[field]:
                related_name = None
                relationship_ids = None
                if many_to_many:
                    related_name = parent_instance._meta.get_field(
                        field
                    ).remote_field.attname
                    relationship_ids = data.pop(related_name)
                else:
                    data[self.parent_id_field] = parent_instance.id
                child_instance = handle_nested_objects(
                    data, kwargs["model"], kwargs["serializer"], partial
                )
                updated_ids.append(child_instance.id)
                handle_many_to_many_objects(
                    child_instance=child_instance,
                    related_name=related_name,
                    relationship_ids=relationship_ids,
                    updated_ids=updated_ids,
                    **kwargs,
                )
        return updated_ids

    def get_obj_data(
        self, nested_field_objects: Dict[str, NestedFieldTypes], validated_data
    ):
        """
        Pull out the required fields (i.e. nested objects field) and return as dict
        """
        obj_data = {}
        for field in nested_field_objects:
            source_field_name = self.get_source_field_name(field)
            if source_field_name in validated_data:
                obj_data[field] = validated_data.pop(source_field_name)
        return obj_data


def handle_many_to_many_objects(**kwargs):
    # Check args and unpack
    check_kwargs(
        [
            "child_instance",
            "parent_instance",
            "related_name",
            "relationship_ids",
            "field",
            "updated_ids",
            "partial",
            "method",
        ],
        kwargs,
    )
    related_name = kwargs["related_name"]
    relationship_ids = kwargs["relationship_ids"]
    parent_instance = kwargs["parent_instance"]
    child_instance = kwargs["child_instance"]
    field = kwargs["field"]
    method = kwargs["method"]
    assert method in ["update", "create"]

    if related_name and relationship_ids:
        if method == "update":
            getattr(child_instance, related_name).set(relationship_ids)
            if kwargs["partial"]:
                getattr(parent_instance, field).add(child_instance)
            else:
                getattr(parent_instance, field).set(kwargs["updated_ids"])
        else:
            getattr(child_instance, related_name).set(relationship_ids)
            getattr(parent_instance, field).add(child_instance)


def handle_nested_objects(data, model, serializer, partial=False):
    """
    Takes a nested object and performs update or create dependent on 'id' being present
    """
    data_id = data.get("id")
    if data_id:
        try:
            obj_instance = model.objects.get(id=data_id)
        except ObjectDoesNotExist as ex:
            raise exceptions.NotFound(
                detail=f"{model.__name__} with id: {data_id} not found."
            ) from ex
        obj_instance = serializer(partial=partial).update(obj_instance, data)
    elif not partial:  # i.e. PUT
        obj_instance = serializer().create(data)
    else:
        raise serializers.ValidationError(
            f"'id' required for nested update to {model.__name__}.", code="bad_request"
        )
    return obj_instance
