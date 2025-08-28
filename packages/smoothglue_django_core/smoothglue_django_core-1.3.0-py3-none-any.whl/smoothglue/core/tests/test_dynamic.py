import unittest
from unittest.mock import Mock, patch

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from rest_framework import exceptions, serializers

from smoothglue.core.serializers.dynamic import (
    DynamicModelSerializer,
    NestedObjectModelSerializer,
    handle_many_to_many_objects,
    handle_nested_objects,
)

UPDATED_OBJECT_TEXT = "Updated Object"


class MockUser(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=100)

    class Meta:
        app_label = "test_app"


class MockProfile(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.OneToOneField(
        MockUser, on_delete=models.CASCADE, related_name="profile"
    )
    bio = models.TextField()

    class Meta:
        app_label = "test_app"


class MockPost(models.Model):
    id = models.IntegerField(primary_key=True)
    author = models.ForeignKey(MockUser, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=100)

    class Meta:
        app_label = "test_app"


class MockTag(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    posts = models.ManyToManyField(MockPost, related_name="tags")

    class Meta:
        app_label = "test_app"


class MockTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = MockTag
        fields = ["id", "name"]


class MockPostSerializer(NestedObjectModelSerializer):
    tags = MockTagSerializer(many=True, required=False)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=MockUser.objects.all(), source="author", write_only=True
    )

    class Meta:
        model = MockPost
        fields = ["id", "title", "tags", "author_id"]

    parent_id_field = "author_id"
    nested_field_config = {
        "tags": {"serializer": MockTagSerializer, "model": MockTag},
    }


class MockPostNestedSerializer(MockPostSerializer):
    pass


class MockUserSerializer(NestedObjectModelSerializer):
    posts = MockPostNestedSerializer(many=True, required=False)
    profile_bio = serializers.CharField(source="profile.bio", required=False)

    class Meta:
        model = MockUser
        fields = ("id", "username", "posts", "profile_bio")

    # For NestedObjectModelSerializer
    parent_id_field = "user_id"
    nested_field_config = {
        "posts": {"serializer": MockPostSerializer, "model": MockPost},
    }


class TestDynamicModelSerializer(unittest.TestCase):
    def setUp(self):
        self.mock_request = Mock()
        self.mock_request.query_params = {}
        self.context = {"request": self.mock_request}

    @patch("smoothglue.core.field_trie.ModifiedTrie")
    def test_init_no_fields_in_request(self, MockModifiedTrie):
        class MySerializer(DynamicModelSerializer):
            field_a = serializers.CharField()
            field_b = serializers.CharField()

            class Meta:
                model = MockUser  # Dummy model
                fields = ["field_a", "field_b"]

        serializer = MySerializer(context=self.context)
        self.assertIn("field_a", serializer.fields)
        self.assertIn("field_b", serializer.fields)
        MockModifiedTrie.return_value.filter_requested_fields.assert_not_called()

    def test_validate_partial_update_with_id_fetches_instance(self):
        class MySerializer(DynamicModelSerializer):
            class Meta:
                model = MockUser
                fields = ["id", "username"]

        mock_user_instance = Mock(id=1, username="testuser")
        MockUser.objects = Mock()
        MockUser.objects.get = Mock(return_value=mock_user_instance)

        serializer = MySerializer(partial=True, context=self.context)
        self.assertIsNone(serializer.instance)

        attrs = {"id": 1, "username": "newname"}
        validated_attrs = serializer.validate(attrs)

        MockUser.objects.get.assert_called_once_with(id=1)
        self.assertEqual(serializer.instance, mock_user_instance)
        self.assertEqual(validated_attrs, attrs)

    def test_validate_patch_request_with_id_fetches_instance(self):
        class MySerializer(DynamicModelSerializer):
            class Meta:
                model = MockUser
                fields = ["id", "username"]

        mock_user_instance = Mock(id=1, username="testuser")
        MockUser.objects = Mock()
        MockUser.objects.get = Mock(return_value=mock_user_instance)

        self.mock_request.method = "PATCH"
        serializer = MySerializer(context=self.context)
        self.assertIsNone(serializer.instance)

        attrs = {"id": 1, "username": "newname"}
        serializer.validate(attrs)

        MockUser.objects.get.assert_called_once_with(id=1)
        self.assertEqual(serializer.instance, mock_user_instance)


class TestNestedObjectModelSerializer(unittest.TestCase):
    def setUp(self):
        self.mock_request = Mock()
        self.mock_request.query_params = {}
        self.context = {"request": self.mock_request}

        import uuid

        unique_suffix = str(uuid.uuid4())[:8]

        class SimpleParentModel(models.Model):
            id = models.IntegerField(primary_key=True)
            name = models.CharField(max_length=50)

            class Meta:
                app_label = f"test_app_parent_{unique_suffix}"

        self.ParentModel = SimpleParentModel

        class SimpleChildModel(models.Model):
            id = models.IntegerField(primary_key=True)
            parent = models.ForeignKey(
                SimpleParentModel, on_delete=models.CASCADE, related_name="children"
            )
            content = models.CharField(max_length=50)

            class Meta:
                app_label = f"test_app_child_{unique_suffix}"

        self.ChildModel = SimpleChildModel

        class SimpleChildSerializer(NestedObjectModelSerializer):
            class Meta:
                model = SimpleChildModel
                fields = ["id", "content", "parent_id"]

            parent_id_field = "parent_id"

            def get_nested_field_config(self):
                return {}

        class SimpleParentSerializer(NestedObjectModelSerializer):
            children = SimpleChildSerializer(many=True, required=False)

            class Meta:
                model = SimpleParentModel
                fields = ["id", "name", "children"]

            parent_id_field = "some_outer_parent_id"
            nested_field_config = {
                "children": {
                    "serializer": SimpleChildSerializer,
                    "model": SimpleChildModel,
                }
            }

        self.ParentSerializer = SimpleParentSerializer
        self.ChildSerializer = SimpleChildSerializer

        self.ParentModel.objects = Mock()
        self.ChildModel.objects = Mock()

    def test_get_parent_id_field_assertion(self):
        class FaultySerializer(NestedObjectModelSerializer):
            class Meta:
                model = self.ParentModel
                fields = "__all__"

            def get_nested_field_config(self):
                return {"some": "config"}

        with self.assertRaisesRegex(
            AssertionError, "should either include a `parent_id_field`"
        ):
            FaultySerializer()

    def test_get_nested_field_config_assertion(self):
        class FaultySerializer(NestedObjectModelSerializer):
            parent_id_field = "some_field"

            class Meta:
                model = self.ParentModel
                fields = "__all__"

        with self.assertRaisesRegex(
            AssertionError, "should either include a `nested_field_config`"
        ):
            FaultySerializer()

    def test_get_source_field_name(self):
        class MySerializer(NestedObjectModelSerializer):
            renamed_field = serializers.CharField(source="original_field")
            normal_field = serializers.CharField()
            parent_id_field = "dummy"
            nested_field_config = {"dummy": {"serializer": Mock(), "model": Mock()}}

            class Meta:
                model = MockUser
                fields = "__all__"

        serializer = MySerializer()
        self.assertEqual(
            serializer.get_source_field_name("renamed_field"), "original_field"
        )
        self.assertEqual(
            serializer.get_source_field_name("normal_field"), "normal_field"
        )

    def test_get_obj_data(self):
        serializer = self.ParentSerializer()
        validated_data = {
            "name": "Parent Name",
            "children": [
                {"content": "Child 1"},
                {"content": "Child 2"},
            ],
            "extra_field": "should be ignored",
        }
        serializer._declared_fields["children"] = Mock(source="children")

        obj_data = serializer.get_obj_data(
            serializer.nested_field_config, validated_data
        )

        self.assertIn("children", obj_data)
        self.assertNotIn("children", validated_data)
        self.assertIn("name", validated_data)

    @patch("smoothglue.core.serializers.dynamic.handle_nested_objects")
    def test_iterate_nested_data_handles_children(self, mock_handle_nested):
        """
        Tests that iterate_nested_data correctly calls helper functions
        for creating and updating nested objects.
        """
        mock_parent_instance = Mock(spec=self.ParentModel)
        mock_parent_instance._meta = Mock()
        mock_parent_instance._meta.get_field.return_value.many_to_many = False

        new_child_data = {"content": "New Child"}
        updated_child_data = {"id": 1, "content": "Updated Child"}
        obj_data = {"children": [updated_child_data, new_child_data]}

        mock_handle_nested.side_effect = [Mock(id=1), Mock(id=2)]

        serializer = self.ParentSerializer(instance=mock_parent_instance)

        updated_ids = serializer.iterate_nested_data(
            obj_data=obj_data,
            parent_instance=mock_parent_instance,
            model=self.ChildModel,
            field="children",
            serializer=self.ChildSerializer,
            method="update",
            partial=True,
        )

        self.assertEqual(mock_handle_nested.call_count, 2)
        mock_handle_nested.assert_any_call(
            updated_child_data, self.ChildModel, self.ChildSerializer, True
        )
        mock_handle_nested.assert_any_call(
            new_child_data, self.ChildModel, self.ChildSerializer, True
        )

        self.assertEqual(len(updated_ids), 2)
        self.assertIn(1, updated_ids)
        self.assertIn(2, updated_ids)

    def test_update_deletes_children_on_non_partial_update(self):
        """
        Tests that the main `update` method calls the deletion logic
        for a non-partial (PUT) update.
        """
        mock_parent_instance = Mock(spec=self.ParentModel, id=1)
        mock_parent_instance._meta = Mock()
        mock_parent_instance._meta.get_field.return_value.many_to_many = False
        mock_parent_instance._meta.get_field.return_value.one_to_one = False

        mock_qs = Mock()
        self.ChildModel.objects.filter.return_value = mock_qs
        mock_qs.exclude.return_value = mock_qs
        mock_qs.all.return_value = [Mock(name="obj_to_delete")]

        validated_data = {"children": [{"id": 1, "content": "Kept Child"}]}

        with patch.object(DynamicModelSerializer, "update") as mock_super_update:
            serializer = self.ParentSerializer(instance=mock_parent_instance)
            serializer.get_obj_data = Mock(return_value=validated_data)
            serializer.iterate_nested_data = Mock(return_value=[1])

            serializer.update(mock_parent_instance, validated_data)

            # Assert deletion logic was called correctly
            self.ChildModel.objects.filter.assert_called_once_with(
                some_outer_parent_id=1
            )
            mock_qs.exclude.assert_called_once_with(pk__in=[1])
            self.assertEqual(mock_qs.all.return_value[0].delete.call_count, 1)

            mock_super_update.assert_called_once()


class TestHelperFunctions(unittest.TestCase):
    def setUp(self):
        self.MockModel = Mock(spec=models.Model)
        self.MockModel.__name__ = "MockModel"
        self.MockModel.objects = Mock()
        self.MockSerializer = Mock(spec=serializers.ModelSerializer)

    def test_handle_nested_objects_create(self):
        data = {"name": "New Object"}
        mock_serializer_instance = Mock()
        mock_created_object = Mock(id=1)
        mock_serializer_instance.create = Mock(return_value=mock_created_object)
        self.MockSerializer.return_value = mock_serializer_instance

        instance = handle_nested_objects(
            data, self.MockModel, self.MockSerializer, partial=False
        )

        self.MockSerializer.assert_called_once_with()
        mock_serializer_instance.create.assert_called_once_with(data)
        self.assertEqual(instance, mock_created_object)
        self.MockModel.objects.get.assert_not_called()

    def test_handle_nested_objects_update(self):
        data = {"id": 1, "name": UPDATED_OBJECT_TEXT}
        mock_existing_object = Mock(id=1)
        mock_updated_object = Mock(id=1, name="Updated Object From Serializer")
        self.MockModel.objects.get = Mock(return_value=mock_existing_object)

        mock_serializer_instance = Mock()
        mock_serializer_instance.update = Mock(return_value=mock_updated_object)
        self.MockSerializer.return_value = mock_serializer_instance

        instance = handle_nested_objects(
            data, self.MockModel, self.MockSerializer, partial=True
        )

        self.MockModel.objects.get.assert_called_once_with(id=1)
        self.MockSerializer.assert_called_once_with(partial=True)
        mock_serializer_instance.update.assert_called_once_with(
            mock_existing_object, data
        )
        self.assertEqual(instance, mock_updated_object)

    def test_handle_nested_objects_update_not_found(self):
        data = {"id": 99, "name": UPDATED_OBJECT_TEXT}
        self.MockModel.objects.get = Mock(side_effect=ObjectDoesNotExist)

        with self.assertRaisesRegex(
            exceptions.NotFound, "MockModel with id: 99 not found."
        ):
            handle_nested_objects(
                data, self.MockModel, self.MockSerializer, partial=True
            )
        self.MockModel.objects.get.assert_called_once_with(id=99)

    def test_handle_nested_objects_partial_update_missing_id_raises_error(self):
        data = {"name": UPDATED_OBJECT_TEXT}
        with self.assertRaisesRegex(
            serializers.ValidationError, "'id' required for nested update to MockModel."
        ):
            handle_nested_objects(
                data, self.MockModel, self.MockSerializer, partial=True
            )

    def test_handle_many_to_many_objects_create_mode(self):
        mock_child_instance = Mock()
        mock_child_instance.tags = Mock()
        mock_parent_instance = Mock()
        mock_parent_instance.posts = Mock()

        kwargs = {
            "child_instance": mock_child_instance,
            "parent_instance": mock_parent_instance,
            "related_name": "tags",
            "relationship_ids": [1, 2],
            "field": "posts",
            "updated_ids": [mock_child_instance.id],
            "partial": False,
            "method": "create",
            "model": Mock(),
            "serializer": Mock(),
        }

        handle_many_to_many_objects(**kwargs)

        mock_child_instance.tags.set.assert_called_once_with([1, 2])
        mock_parent_instance.posts.add.assert_called_once_with(mock_child_instance)
        mock_parent_instance.posts.set.assert_not_called()  # Not for create

    def test_handle_many_to_many_objects_update_mode_partial(self):
        mock_child_instance = Mock()
        mock_child_instance.tags = Mock()
        mock_parent_instance = Mock()
        mock_parent_instance.posts = Mock()

        kwargs = {
            "child_instance": mock_child_instance,
            "parent_instance": mock_parent_instance,
            "related_name": "tags",
            "relationship_ids": [3, 4],
            "field": "posts",
            "updated_ids": [mock_child_instance.id, 99],
            "partial": True,
            "method": "update",
            "model": Mock(),
            "serializer": Mock(),
        }

        handle_many_to_many_objects(**kwargs)

        mock_child_instance.tags.set.assert_called_once_with([3, 4])
        mock_parent_instance.posts.add.assert_called_once_with(mock_child_instance)
        mock_parent_instance.posts.set.assert_not_called()

    def test_handle_many_to_many_objects_update_mode_not_partial(self):
        mock_child_instance = Mock()
        mock_child_instance.tags = Mock()
        mock_parent_instance = Mock()
        mock_parent_instance.posts = Mock()
        updated_child_ids = [mock_child_instance.id, 99]

        kwargs = {
            "child_instance": mock_child_instance,
            "parent_instance": mock_parent_instance,
            "related_name": "tags",
            "relationship_ids": [5, 6],
            "field": "posts",
            "updated_ids": updated_child_ids,
            "partial": False,
            "method": "update",
            "model": Mock(),
            "serializer": Mock(),
        }

        handle_many_to_many_objects(**kwargs)

        mock_child_instance.tags.set.assert_called_once_with([5, 6])
        mock_parent_instance.posts.add.assert_not_called()
        mock_parent_instance.posts.set.assert_called_once_with(updated_child_ids)
