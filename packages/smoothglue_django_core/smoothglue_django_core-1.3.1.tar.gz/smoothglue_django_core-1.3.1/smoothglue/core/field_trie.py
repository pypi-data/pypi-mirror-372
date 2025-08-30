from collections import OrderedDict

from rest_framework.serializers import BindingDict


class ModifiedTrieNode:  # pylint: disable=too-few-public-methods
    def __init__(self, value=None, end_of_field=False, fields_dict=None):
        self.value = value
        self.children = {}
        self.end = end_of_field
        self.fields_dict = fields_dict


class ModifiedTrie:
    """
    Recieves a list of strings, each ele in list will be split by
    a '.' and inserted into the trie. The trie will be used to store
    requested fields, eliminate duplicates of the requested fields
    and allow for removing fields that differ between database
    fields and requested fields
    """

    def __init__(self):
        self.__root = ModifiedTrieNode()

    def insert(self, requested_field_section):
        current = self.__root
        for field in requested_field_section.split("."):
            current = current.children.setdefault(field, ModifiedTrieNode(field))
        current.end = True

    def filter_requested_fields(self, fields_dict: BindingDict):
        """
        Traverse tree (breadth) and at each level, compare level
        against the database fields and remove differences. While
        traversing, add node and children(unless node is end) to
        queue. Also pass the database fields
        """

        self.__root.fields_dict = fields_dict  # self.fields
        is_root = True  # accessing fields is different for top level vs nested

        field_queue = [self.__root]
        while field_queue:
            current = field_queue.pop(0)

            if not current.end:  # this stops from traversing lower
                if is_root:
                    default_fields = OrderedDict(current.fields_dict).keys()
                    is_root = False
                elif hasattr(current.fields_dict, "get_fields"):
                    default_fields = current.fields_dict.get_fields().keys()
                else:
                    # a NestedBoundField that doesn't render in time,
                    # i.e. request_allocations/?fields=fuel_request.asset.fuel_requests.id
                    continue

                self.compare_children_to_default_fields(
                    current, default_fields, field_queue
                )

    def compare_children_to_default_fields(
        self, current: ModifiedTrieNode, default_fields, field_queue
    ):
        currents_children = []
        actual_children_field_container = current.fields_dict.fields
        for node in current.children.values():
            if node.value in default_fields:
                node.fields_dict = actual_children_field_container[str(node.value)]

                field_queue.append(node)
                currents_children.append(node.value)

        for field_name in default_fields - set(currents_children):
            current.fields_dict.fields.pop(field_name)
