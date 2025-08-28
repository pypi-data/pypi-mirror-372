import unittest
from collections import OrderedDict

from smoothglue.core.field_trie import ModifiedTrie, ModifiedTrieNode


class MockField:
    """
    A simplified mock for a serializer field.
    It can have nested fields accessible via get_fields() or be a simple value.
    """

    def __init__(self, is_nested=False, nested_fields=None):
        self._is_nested = is_nested
        if is_nested and nested_fields:
            self.fields = OrderedDict(nested_fields)
        elif is_nested:
            self.fields = OrderedDict()

    def get_fields(self):
        if self._is_nested:
            return self.fields
        raise AttributeError(
            "This mock field is not a nested serializer and has no 'get_fields' method."
        )


class MockBindingDict(OrderedDict):
    """
    A simplified mock for DRF's BindingDict.
    It behaves like an OrderedDict and holds MockField instances.
    It also needs a 'fields' attribute that points to itself for
    the pop operation in `compare_children_to_default_fields`.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = self

    def get_fields(self):
        return self


class TestModifiedTrieNode(unittest.TestCase):
    def test_node_initialization_default(self):
        node = ModifiedTrieNode()
        self.assertIsNone(node.value)
        self.assertEqual(node.children, {})
        self.assertFalse(node.end)
        self.assertIsNone(node.fields_dict)

    def test_node_initialization_with_values(self):
        mock_fields = {"key": "value"}
        node = ModifiedTrieNode(
            value="test", end_of_field=True, fields_dict=mock_fields
        )
        self.assertEqual(node.value, "test")
        self.assertEqual(node.children, {})
        self.assertTrue(node.end)
        self.assertEqual(node.fields_dict, mock_fields)


class TestModifiedTrie(unittest.TestCase):
    def setUp(self):
        self.trie = ModifiedTrie()
        self.USER_NAME = "user.name"
        self.USER_USERNAME = "user.username"

    def test_initialization(self):
        self.assertIsNotNone(self.trie._ModifiedTrie__root)
        self.assertIsNone(self.trie._ModifiedTrie__root.value)
        self.assertEqual(self.trie._ModifiedTrie__root.children, {})

    def test_insert_single_field(self):
        self.trie.insert("id")
        self.assertIn("id", self.trie._ModifiedTrie__root.children)
        id_node = self.trie._ModifiedTrie__root.children["id"]
        self.assertEqual(id_node.value, "id")
        self.assertTrue(id_node.end)
        self.assertEqual(id_node.children, {})

    def test_insert_nested_field(self):
        self.trie.insert("user.profile.image")
        user_node = self.trie._ModifiedTrie__root.children.get("user")
        self.assertIsNotNone(user_node)
        self.assertEqual(user_node.value, "user")
        self.assertFalse(user_node.end)

        profile_node = user_node.children.get("profile")
        self.assertIsNotNone(profile_node)
        self.assertEqual(profile_node.value, "profile")
        self.assertFalse(profile_node.end)

        image_node = profile_node.children.get("image")
        self.assertIsNotNone(image_node)
        self.assertEqual(image_node.value, "image")
        self.assertTrue(image_node.end)
        self.assertEqual(image_node.children, {})

    def test_insert_multiple_fields_shared_prefix(self):
        self.trie.insert(self.USER_NAME)
        self.trie.insert("user.email")
        self.trie.insert("post.title")

        user_node = self.trie._ModifiedTrie__root.children.get("user")
        self.assertIsNotNone(user_node)
        self.assertIn("name", user_node.children)
        self.assertIn("email", user_node.children)
        self.assertTrue(user_node.children["name"].end)
        self.assertTrue(user_node.children["email"].end)

        post_node = self.trie._ModifiedTrie__root.children.get("post")
        self.assertIsNotNone(post_node)
        self.assertIn("title", post_node.children)
        self.assertTrue(post_node.children["title"].end)

    def test_insert_duplicate_field(self):
        self.trie.insert(self.USER_NAME)
        self.trie.insert(self.USER_NAME)  # Insert again

        user_node = self.trie._ModifiedTrie__root.children.get("user")
        name_node = user_node.children.get("name")
        self.assertTrue(name_node.end)
        # Ensure no duplicate nodes
        self.assertEqual(len(user_node.children), 1)

    def test_filter_requested_fields_empty_trie(self):
        # if nothing is requested, and nothing is default, nothing happens.
        # More accurately, if nothing requested, all default fields are popped).
        initial_fields = MockBindingDict({"id": MockField(), "name": MockField()})
        self.trie.filter_requested_fields(initial_fields)
        self.assertEqual(len(initial_fields), 0)

    def test_filter_requested_fields_no_matching_root_fields(self):
        self.trie.insert("nonexistent_field")
        initial_fields = MockBindingDict({"id": MockField(), "name": MockField()})
        self.trie.filter_requested_fields(initial_fields)
        # "id" and "name" were not requested through the trie (nonexistent_field was)
        # so "id" and "name" should be popped.
        self.assertEqual(len(initial_fields), 0)

    def test_filter_requested_fields_simple_match(self):
        self.trie.insert("name")
        initial_fields = MockBindingDict(
            {"id": MockField(), "name": MockField(), "email": MockField()}
        )
        self.trie.filter_requested_fields(initial_fields)
        self.assertIn("name", initial_fields)
        self.assertNotIn("id", initial_fields)
        self.assertNotIn("email", initial_fields)
        self.assertEqual(len(initial_fields), 1)

    def test_filter_requested_fields_nested_match(self):
        self.trie.insert("user.profile.image_url")
        self.trie.insert(self.USER_USERNAME)

        initial_fields = MockBindingDict(
            {
                "id": MockField(),
                "user": MockField(
                    is_nested=True,
                    nested_fields={
                        "username": MockField(),
                        "email": MockField(),  # Not requested
                        "profile": MockField(
                            is_nested=True,
                            nested_fields={
                                "image_url": MockField(),
                                "bio": MockField(),  # Not requested
                            },
                        ),
                    },
                ),
                "post_count": MockField(),  # Not requested
            }
        )

        self.trie.filter_requested_fields(initial_fields)

        self.assertNotIn("id", initial_fields)
        self.assertNotIn("post_count", initial_fields)
        self.assertIn("user", initial_fields)

        user_field_data = initial_fields["user"]
        self.assertIn("username", user_field_data.fields)
        self.assertNotIn("email", user_field_data.fields)
        self.assertIn("profile", user_field_data.fields)

        profile_field_data = user_field_data.fields["profile"]
        self.assertIn("image_url", profile_field_data.fields)
        self.assertNotIn("bio", profile_field_data.fields)

    def test_filter_requested_fields_partial_nested_match(self):

        self.trie.insert("user")

        initial_fields = MockBindingDict(
            {
                "user": MockField(
                    is_nested=True,
                    nested_fields={"username": MockField(), "email": MockField()},
                )
            }
        )

        self.trie.filter_requested_fields(initial_fields)

        self.assertIn("user", initial_fields)
        user_field_data = initial_fields["user"]
        self.assertIn("username", user_field_data.fields)
        self.assertIn("email", user_field_data.fields)

    def test_filter_requested_fields_request_parent_and_specific_child(self):
        self.trie.insert(self.USER_USERNAME)

        initial_fields = MockBindingDict(
            {
                "user": MockField(
                    is_nested=True,
                    nested_fields={
                        "username": MockField(),
                        "email": MockField(),  # This should be pruned
                        "status": MockField(),  # This should be pruned
                    },
                ),
                "other_field": MockField(),  # This should be pruned
            }
        )

        self.trie.filter_requested_fields(initial_fields)

        self.assertNotIn("other_field", initial_fields)
        self.assertIn("user", initial_fields)
        user_field_data = initial_fields["user"]

        self.assertIn("username", user_field_data.fields)
        self.assertNotIn("email", user_field_data.fields)
        self.assertNotIn("status", user_field_data.fields)

    def test_filter_requested_fields_non_existent_nested_field_in_trie(self):
        self.trie.insert("user.profile.non_existent_detail")

        initial_fields = MockBindingDict(
            {
                "user": MockField(
                    is_nested=True,
                    nested_fields={
                        "username": MockField(),
                        "profile": MockField(
                            is_nested=True, nested_fields={"image_url": MockField()}
                        ),
                    },
                )
            }
        )
        self.trie.filter_requested_fields(initial_fields)

        self.assertIn("user", initial_fields)
        user_field_data = initial_fields["user"]
        self.assertIn("profile", user_field_data.fields)
        profile_field_data = user_field_data.fields["profile"]

        # image_url was not requested, so it's removed.
        self.assertNotIn("image_url", profile_field_data.fields)
        self.assertEqual(len(profile_field_data.fields), 0)

    def test_filter_requested_fields_field_without_get_fields(self):
        self.trie.insert("problem_field.child")

        class MockNonNestedFieldWithChildrenInTrie:
            # This mock won't have 'get_fields'.
            # It also won't have a 'fields' attribute like MockField(is_nested=True)
            # For the pop operation, the original code relies on current.fields_dict.fields.pop()
            # So, the parent (problem_field's dict) must have .fields
            pass

        initial_fields = MockBindingDict(
            # problem_field does not have .get_fields()
            {
                "problem_field": MockNonNestedFieldWithChildrenInTrie(),
                "another_field": MockField(),
            }
        )
        # The 'problem_field' node in the trie will have a child 'child'.
        # When processing 'problem_field',
        # current.fields_dict will be MockNonNestedFieldWithChildrenInTrie.
        # hasattr(current.fields_dict, "get_fields") will be False.
        # The `continue` should be hit. 'another_field' should be popped.
        self.trie.filter_requested_fields(initial_fields)

        self.assertIn(
            "problem_field", initial_fields
        )  # Kept because it was in trie, but children not processed
        self.assertNotIn("another_field", initial_fields)  # Removed as not requested

    def test_compare_children_to_default_fields_all_children_match(self):
        # Setup parent node and its children in the trie
        parent_node = ModifiedTrieNode("parent")
        child1_node = ModifiedTrieNode("child1")
        child2_node = ModifiedTrieNode("child2")
        parent_node.children = {"child1": child1_node, "child2": child2_node}

        parent_fields_dict_fields_attr = MockBindingDict(
            {
                "child1": MockField(
                    is_nested=True, nested_fields={"sub1": MockField()}
                ),
                "child2": MockField(),
                "extra_in_dict": MockField(),  # This should be removed
            }
        )

        parent_node.fields_dict = MockField(
            is_nested=True, nested_fields=parent_fields_dict_fields_attr
        )
        parent_node.fields_dict.fields = parent_fields_dict_fields_attr

        default_db_fields = {"child1", "child2", "extra_in_dict"}
        field_queue = []

        self.trie.compare_children_to_default_fields(
            parent_node, default_db_fields, field_queue
        )

        self.assertIsNotNone(child1_node.fields_dict)
        self.assertEqual(
            child1_node.fields_dict, parent_fields_dict_fields_attr["child1"]
        )
        self.assertIsNotNone(child2_node.fields_dict)
        self.assertEqual(
            child2_node.fields_dict, parent_fields_dict_fields_attr["child2"]
        )

        self.assertIn(child1_node, field_queue)
        self.assertIn(child2_node, field_queue)

        self.assertNotIn("extra_in_dict", parent_node.fields_dict.fields)
        self.assertIn("child1", parent_node.fields_dict.fields)
        self.assertIn("child2", parent_node.fields_dict.fields)

    def test_compare_children_to_default_fields_some_children_not_in_defaults(self):
        parent_node = ModifiedTrieNode("parent")
        child1_node = ModifiedTrieNode("child1")  # in defaults
        child_not_in_defaults_node = ModifiedTrieNode(
            "child_not_in_defaults"
        )  # NOT in defaults
        parent_node.children = {
            "child1": child1_node,
            "child_not_in_defaults": child_not_in_defaults_node,
        }

        parent_fields_dict_fields_attr = MockBindingDict(
            {
                "child1": MockField(),
                "other_field_in_dict": MockField(),
            }
        )
        parent_node.fields_dict = MockField(
            is_nested=True, nested_fields=parent_fields_dict_fields_attr
        )
        parent_node.fields_dict.fields = parent_fields_dict_fields_attr

        default_db_fields = {
            "child1",
            "other_field_in_dict",
        }  # child_not_in_defaults is not here
        field_queue = []

        self.trie.compare_children_to_default_fields(
            parent_node, default_db_fields, field_queue
        )

        self.assertIsNotNone(child1_node.fields_dict)
        self.assertIsNone(
            child_not_in_defaults_node.fields_dict
        )  # Not in defaults, so not processed

        self.assertIn(child1_node, field_queue)
        self.assertNotIn(child_not_in_defaults_node, field_queue)

        # 'other_field_in_dict' was in default_db_fields
        # but not in parent_node.children, so it's removed.
        self.assertNotIn("other_field_in_dict", parent_node.fields_dict.fields)
        self.assertIn("child1", parent_node.fields_dict.fields)

    def test_filter_root_level_fields_correctly_when_is_root_true(self):
        self.trie.insert("name")
        # initial_fields is the root fields_dict
        initial_fields = MockBindingDict(
            {
                "id": MockField(),
                "name": MockField(is_nested=False),  # Mark as not nested for clarity
                "email": MockField(),
            }
        )

        # Ensure the root node's fields_dict is set to initial_fields
        self.trie._ModifiedTrie__root.fields_dict = initial_fields

        self.trie.filter_requested_fields(initial_fields)

        self.assertIn("name", initial_fields)
        self.assertNotIn(
            "id", initial_fields
        )  # Popped by compare_children called on root
        self.assertNotIn(
            "email", initial_fields
        )  # Popped by compare_children called on root
        self.assertEqual(len(initial_fields), 1)

        name_node = self.trie._ModifiedTrie__root.children["name"]
        self.assertEqual(name_node.fields_dict, initial_fields["name"])

    def test_filter_nested_fields_with_get_fields(self):
        self.trie.insert(self.USER_USERNAME)
        nested_user_fields = OrderedDict(
            {"username": MockField(), "email": MockField()}
        )
        user_mock_field = MockField(is_nested=True, nested_fields=nested_user_fields)

        initial_fields = MockBindingDict({"user": user_mock_field, "id": MockField()})

        self.trie.filter_requested_fields(initial_fields)

        self.assertIn("user", initial_fields)
        self.assertNotIn("id", initial_fields)

        user_data_after_filter = initial_fields["user"]
        self.assertIn("username", user_data_after_filter.fields)
        self.assertNotIn("email", user_data_after_filter.fields)

        user_node = self.trie._ModifiedTrie__root.children["user"]
        username_node = user_node.children["username"]
        self.assertEqual(username_node.fields_dict, nested_user_fields["username"])
