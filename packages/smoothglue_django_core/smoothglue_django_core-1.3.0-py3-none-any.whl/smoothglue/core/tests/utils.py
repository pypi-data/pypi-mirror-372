import copy
import json
import types
from collections.abc import MutableMapping
from typing import Any, Dict, List, Type, TypeVar
from uuid import UUID

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model
from django.test import Client, TestCase
from rest_framework.serializers import BaseSerializer
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.viewsets import ModelViewSet

T = TypeVar("T")


def convert_dict_value_types(dictionary, value_type, convert_type):
    # Convert the type of any value in a dictionary
    for key, val in dictionary.items():
        if isinstance(val, value_type):
            dictionary[key] = convert_type(val)
    return dictionary


class CommonSerializer:
    def __init__(self, serializer: Type[BaseSerializer], context: dict = None):
        self.serializer = serializer
        self.test_case = TestCase()
        self.context = context

    def test_model_serializer_valid(
        self,
        model: Type[Model],
        required_fields: List[str],
        data: Dict[str, T],
    ):
        self.test_required_fields(required_fields, data)
        ser = self.serializer(data=data)
        if self.context:
            ser.context.update(self.context)
        self.test_case.assertTrue(
            ser.is_valid(), msg=f"Serializer data not valid for {data}\n{ser.errors}"
        )
        instance = ser.save()
        model_qs = model.objects.filter(id=instance.id)
        self.test_case.assertEqual(len(model_qs), 1)
        self.test_case.assertEqual(model_qs.all()[0].id, instance.id)

    def test_required_fields(self, required_fields: List[str], data: Dict[str, T]):
        for field in required_fields:
            data_copy = copy.deepcopy(data)
            del data_copy[field]
            ser = self.serializer(data=data_copy)

            self.test_case.assertFalse(
                expr=ser.is_valid(),
                msg=f"Required field not checked: {field}\n{ser.errors}",
            )


class CommonAPI:
    def __init__(self, client: Client):
        self.client = client
        self.test_case = TestCase()

    # pylint: disable=R0913
    def test_get_list(
        self,
        object_data: List[Dict[str, T]],
        model: Type[Model],
        endpoint: str,
        update_fields: Dict[str, Any] = None,
        ignore_object_keys: list[str] = None,
    ):
        created_objects = [model.objects.create(**d) for d in object_data]

        response = self.client.get(endpoint, format="json")
        self.test_case.assertEqual(response.status_code, 200)
        if ignore_object_keys:
            response_data = [
                self._delete_keys_from_dict(item, ignore_object_keys)
                for item in response.json()
            ]
        else:
            response_data = response.json()
        self.test_case.assertEqual(
            len(response_data),
            len(object_data),
            msg="Expected number of objects differs from number in response.",
        )

        # Get ids of objects and from response to compare
        response_ids = {d.pop("id") for d in response_data}
        obj_ids = {str(obj.id) for obj in created_objects}
        self.test_case.assertEqual(response_ids, obj_ids)

        for obj_dict in object_data:
            if update_fields:
                obj_dict.update(update_fields)
            # NOTE: Object IDs removed from response before comparison
            self.test_case.assertTrue(
                obj_dict in response_data,
                msg=f"\nObject:\n{obj_dict}\nnot found in response:\n{response_data}",
            )

    # pylint: disable=R0913
    def test_get_filter_list(
        self,
        object_data: List[Dict[str, T]],
        model: Type[Model],
        endpoint: str,
        filter_name: str,
        filter_value: str,
        assertion_override_func: types.FunctionType = None,
    ):
        for d in object_data:
            model.objects.create(**d)

        response = self.client.get(endpoint, format="json")

        filtered_endpoint = f"{endpoint}?{filter_name}={filter_value}"
        filtered_response = self.client.get(filtered_endpoint, format="json")
        self.test_case.assertEqual(response.status_code, 200)
        self.test_case.assertEqual(filtered_response.status_code, 200)

        # Get properties based on filter name and check for equality
        if assertion_override_func is None:
            self.test_case.assertNotEqual(
                len(response.json()),
                len(filtered_response.json()),
                msg="Expected number of objects are the same in filtered response.",
            )

            response_values = {d.pop(filter_name) for d in filtered_response.json()}
            for value in response_values:
                self.test_case.assertEqual(
                    value,
                    filter_value,
                    msg=f"\nFilter error: {value} is not the filtered value {filter_value}",
                )
        else:
            # This is mainly for adding support for asserting nested filters, which the
            # nested filter value are sometimes not included in the response.
            assertion_override_func(filtered_response, self.test_case)

    def test_post_create(
        self,
        object_data: Dict[str, T],
        endpoint: str,
        update_fields: Dict[str, Any] = None,
        ignore_object_keys: list[str] = None,
    ):
        response = self.client.post(endpoint, data={}, format="json")
        self.test_case.assertEqual(response.status_code, 400)

        response = self.client.post(endpoint, data=object_data, format="json")
        self.test_case.assertEqual(
            response.status_code, 201, msg=(f"Response Data:\n{response.data}")
        )

        if update_fields:
            object_data.update(update_fields)

        response.json().pop("id")
        self.test_case.assertEqual(
            object_data,
            self._delete_keys_from_dict(response.json(), ignore_object_keys),
        )

    def test_post_create_nested(
        self,
        object_data: Dict[str, Any],
        update_data: Dict[str, List[Dict[str, Any]]],
        endpoint: str,
    ):
        """Test the creation of nested objects in a single POST"""
        for field in update_data:
            for i, data in enumerate(update_data[field]):  # Get nested object
                for nested_field in data:
                    object_copy = copy.deepcopy(object_data)
                    update_copy = copy.deepcopy(update_data)
                    data_copy = data.copy()
                    del data_copy[nested_field]
                    update_copy[field][i] = data_copy
                    object_copy[field] = update_copy[field]

                    response = self.client.post(
                        endpoint, data=object_copy, format="json"
                    )
                    self.test_case.assertEqual(
                        response.status_code,
                        400,
                        msg=(
                            f"Creation of partial nested objects should not be valid "
                            f"(missing '{nested_field}'):\n{response.data}"
                        ),
                    )

        object_data.update(**update_data)

        response = self.client.post(endpoint, data=object_data, format="json")
        self.test_case.assertEqual(
            response.status_code,
            201,
            msg=(
                "Nested objects for creation should be valid.\n"
                f"Response Data:\n{response.data}"
            ),
        )

    def test_post_create_list(
        self,
        object_data: List[Dict[str, T]],
        endpoint: str,
        update_fields: Dict[str, Any] = None,
    ):
        response = self.client.post(endpoint, data=object_data, format="json")
        self.test_case.assertEqual(response.status_code, 201)
        self.test_case.assertEqual(len(response.json()), len(object_data))

        for response_obj in response.json():
            del response_obj["id"]

        for obj in object_data:
            if update_fields:
                obj.update(update_fields)
            self.test_case.assertTrue(
                obj in response.json(),
                f"Could not find\n{obj}\nin response:\n{response.json()}",
            )

    def test_get_by_id(
        self,
        object_data: Dict[str, T],
        model: Type[Model],
        endpoint: str,
        update_fields: Dict[str, Any] = None,
    ):
        # Create the object in db first
        created_object = model.objects.create(**object_data)
        response = self.client.get(f"{endpoint}{created_object.id}/", format="json")

        self.test_case.assertEqual(response.status_code, 200)

        del response.json()["id"]
        if update_fields:
            object_data.update(update_fields)
        self.test_case.assertEqual(object_data, response.json())

    def test_post_empty_nested_objects(
        self,
        object_data: Dict[str, T],
        nested_field_names: List[str],
        endpoint: str,
    ):
        for field_name in nested_field_names:
            object_copy = copy.deepcopy(object_data)
            object_copy.update(**{field_name: [{}]})
            response = self.client.post(endpoint, data=object_copy, format="json")
            self.test_case.assertEqual(
                response.status_code,
                400,
                msg="Empty nested objects should not be valid",
            )

    def test_put(
        self,
        original_object: T,
        new_data: Dict[str, T],
        endpoint: str,
        update_fields: Dict[str, Any] = None,
        ignore_object_keys: list[str] = None,
    ):
        response = self.client.put(endpoint, data=new_data, format="json")
        self.test_case.assertEqual(response.status_code, 200)

        # Test that we are doing PUT against the same object while also deleting ID from response
        self.test_case.assertEqual(str(original_object.id), response.json().pop("id"))

        if update_fields:
            new_data.update(update_fields)
        self.test_case.assertEqual(
            new_data, self._delete_keys_from_dict(response.json(), ignore_object_keys)
        )

    @staticmethod
    def _clean_up_nested_create(
        response, field, original_id, original_ids, update_data
    ):
        """
        Replaces ONE deleted object with a created one (from nested PUT replace)
        Updates 'update_data' in place
        """
        complete = False
        for obj in response.data[field]:
            if UUID(obj["id"]) not in original_ids:
                for j, update_obj in enumerate(update_data[field]):
                    if update_obj["id"] == original_id:
                        update_data[field][j] = obj
                        complete = True
                        break
            if complete:
                break

    @staticmethod
    def _get_original_ids(data):
        """
        Grabs all ids in a list of objects, converting them to UUID if necessary
        """
        return [
            obj["id"] if isinstance(obj["id"], UUID) else UUID(obj["id"])
            for obj in data
        ]

    @staticmethod
    def _delete_keys_from_dict(dictionary, keys):
        if keys is None:
            return dictionary

        keys_set = set(keys)  # Just an optimization for the "if key in keys" lookup.

        modified_dict = {}
        for key, value in dictionary.items():
            if key not in keys_set:
                if isinstance(value, MutableMapping):
                    modified_dict[key] = CommonAPI._delete_keys_from_dict(
                        value, keys_set
                    )
                else:
                    modified_dict[key] = (
                        value  # or copy.deepcopy(value) if a copy is desired for non-dicts.
                    )
        return modified_dict

    def test_put_nested(
        self,
        object_data: Dict[str, Any],
        update_data: Dict[str, List[Dict[str, Any]]],
        endpoint: str,
    ):
        """
        Test update to nested objects in a single PUT

        Expects a list of nested objects with ALL required fields
        """
        for field in update_data:
            for i, data in enumerate(update_data[field]):  # Get nested object
                for nested_field in data:
                    object_copy = copy.deepcopy(object_data)
                    update_copy = copy.deepcopy(update_data)
                    data_copy = data.copy()
                    del data_copy[nested_field]  # Delete a required field
                    update_copy[field][
                        i
                    ] = data_copy  # Replace the nested object to test
                    object_copy.update(update_copy)

                    response = self.client.put(
                        endpoint, data=object_copy, format="json"
                    )
                    if nested_field == "id":
                        # Get all original ids for cleanup later
                        original_id = data["id"]
                        original_ids = self._get_original_ids(update_data[field])
                        self.test_case.assertEqual(
                            response.status_code,
                            200,
                            msg=(
                                f"Nested creation (without 'id' field) should be valid on PUT "
                                f":\n{response.data}"
                            ),
                        )
                        # Cleanup data by replacing update data with created obj
                        self._clean_up_nested_create(
                            response, field, original_id, original_ids, update_data
                        )
                    else:
                        self.test_case.assertEqual(
                            response.status_code,
                            400,
                            msg=(
                                f"Partial nested updates should not be valid on PUT "
                                f"(missing '{nested_field}'):\n{response.data}"
                            ),
                        )

        object_data.update(**update_data)

        response = self.client.put(endpoint, data=object_data, format="json")
        self.test_case.assertEqual(
            response.status_code,
            200,
            msg=f"Nested objects for full update should be valid:\n{response.data}",
        )

    def test_patch(
        self, new_data: Dict[str, T], expected_data: Dict[str, T], endpoint: str
    ):
        response = self.client.patch(endpoint, data=new_data, format="json")
        self.test_case.assertEqual(
            response.status_code,
            200,
            msg=("Expected status 200.\n" f"Response Data:\n{response.data}"),
        )
        self.test_case.assertEqual(expected_data, response.json())

    def test_patch_nested(
        self,
        object_data: Dict[str, Any],
        update_data: Dict[str, List[Dict[str, Any]]],
        endpoint: str,
    ):
        """
        Test partial update to nested objects in single PATCH

        Expects a list of nested objects with ALL required fields
        """
        for field in update_data:
            for i, data in enumerate(update_data[field]):  # Get nested object
                for nested_field in data:
                    object_copy = copy.deepcopy(object_data)
                    update_copy = copy.deepcopy(update_data)
                    data_copy = data.copy()
                    del data_copy[nested_field]
                    update_copy[field][i] = data_copy
                    object_copy[field] = update_copy[field]

                    response = self.client.patch(
                        endpoint, data=object_copy, format="json"
                    )
                    if nested_field == "id":
                        self.test_case.assertEqual(
                            response.status_code,
                            400,
                            msg=(
                                f"'id' required for partial update to nested objects:"
                                f"\n{response.data}"
                            ),
                        )
                    else:
                        self.test_case.assertEqual(
                            response.status_code,
                            200,
                            msg=(
                                f"Partial updates to nested objects should be valid "
                                f"(missing '{nested_field}'):\n{response.data}"
                            ),
                        )

        object_data.update(**update_data)
        response = self.client.patch(endpoint, data=object_data, format="json")
        self.test_case.assertEqual(response.status_code, 200, response.data)

    def test_delete(self, original_object: T, model: Type[Model], endpoint: str):
        response = self.client.delete(endpoint, format="json")
        self.test_case.assertEqual(response.status_code, 204)
        with self.test_case.assertRaises(ObjectDoesNotExist):
            model.objects.get(id=original_object.id)


class CommonView:
    def __init__(self, user: T, view_set: Type[ModelViewSet]):
        self.standard_config = {
            "get": "list",
            "post": "create",
            "get_id": "retrieve",
            "put": "update",
            "patch": "partial_update",
            "delete": "destroy",
        }
        self.test_case = TestCase()
        self.factory = APIRequestFactory()
        self.content_type = "application/json"
        self.user = user
        self.view = view_set.as_view(actions=self.standard_config)

    def test_get_list(self, objects: List[T], serializer: Type[BaseSerializer]):
        request = self.factory.get("")
        force_authenticate(request, user=self.user)
        response = self.view(request)
        self.test_case.assertEqual(response.status_code, 200)

        for obj in objects:
            self.test_case.assertTrue(
                serializer(obj).data in response.data,
                msg=(
                    f"TeamLead object data should be in response.\n"
                    f"Object:\n{serializer(obj).data}\nResponse:\n{response.data}"
                ),
            )

    def test_get_id(self, obj: T, serializer: Type[BaseSerializer]):
        request = self.factory.get(f"/{obj.id}/")
        force_authenticate(request, user=self.user)
        response = self.view(request)
        self.test_case.assertEqual(response.status_code, 200)
        self.test_case.assertEqual(serializer(obj).data, response.data[0])

    def test_post(
        self,
        obj_data: Dict[str, T],
        non_required_fields: Dict[str, T] = None,
    ):
        request = self.factory.post(
            "", data=json.dumps(obj_data), content_type=self.content_type
        )
        force_authenticate(request, user=self.user)
        response = self.view(request)
        self.test_case.assertEqual(response.status_code, 201)

        if non_required_fields:
            obj_data.update(non_required_fields)
        del response.data["id"]
        response.data = convert_dict_value_types(response.data, UUID, str)
        self.test_case.assertEqual(obj_data, response.data)

    def test_post_list(
        self,
        objects_data: List[Dict[str, T]],
        non_required_fields: Dict[str, T] = None,
    ):
        request = self.factory.post(
            "", data=json.dumps(objects_data), content_type=self.content_type
        )
        force_authenticate(request, user=self.user)
        response = self.view(request)
        self.test_case.assertEqual(response.status_code, 201)

        for i, data in enumerate(response.data):
            del data["id"]
            response.data[i] = convert_dict_value_types(data, UUID, str)

        for obj_data in objects_data:
            obj_data.update(non_required_fields)
            self.test_case.assertTrue(obj_data in response.data)

    def test_put(
        self,
        obj: T,
        update_data: Dict[str, T],
        model: Type[Model],
        serializer: Type[BaseSerializer],
    ):
        request = self.factory.put(
            f"/{obj.id}/", data=json.dumps(update_data), content_type=self.content_type
        )
        force_authenticate(request, user=self.user)
        response = self.view(request, pk=obj.id)
        self.test_case.assertEqual(response.status_code, 200)

        obj = model.objects.get(id=obj.id)
        self.test_case.assertEqual(serializer(obj).data, response.data)

    def test_patch(
        self,
        obj: T,
        update_data: Dict[str, T],
        model: Type[Model],
        serializer: Type[BaseSerializer],
    ):
        request = self.factory.patch(
            f"/{obj.id}/", data=json.dumps(update_data), content_type="application/json"
        )
        force_authenticate(request, user=self.user)
        response = self.view(request, pk=obj.id)
        self.test_case.assertEqual(response.status_code, 200)

        team_lead = model.objects.get(id=obj.id)
        self.test_case.assertEqual(serializer(team_lead).data, response.data)

    def test_delete(self, obj: T):
        request = self.factory.delete(f"/{obj.id}/")
        force_authenticate(request, user=self.user)
        response = self.view(request, pk=obj.id)
        self.test_case.assertEqual(response.status_code, 204)


class CommonMigrator:
    def __init__(self):
        self.test_case = TestCase()

    @staticmethod
    def get_json(objects):
        return json.loads(serializers.serialize("json", objects))

    def _compare_old_new_data(self, old_data, new_data):
        """
        Expects list of serialized json objects to be compared 1:1
        with the exception of the 'model' field which should be different
        """
        self.test_case.assertEqual(len(old_data), len(new_data))
        for old_obj in old_data:
            found = False
            for new_obj in new_data:
                if new_obj["pk"] == old_obj["pk"]:
                    self.test_case.assertNotEqual(
                        old_obj.pop("model"), new_obj.pop("model")
                    )
                    self.test_case.assertEqual(old_obj, new_obj)
                    found = True
                    break
            self.test_case.assertTrue(
                found, msg=f"{old_obj} not found in new data transfer"
            )

    def test_objects_transferred(
        self, test_map, new_state, new_app_label, old_app_label
    ):
        # Check that all objects transferred
        for model_name, old_data in test_map.items():
            NewModel = new_state.apps.get_model(new_app_label, model_name)
            new_data = json.loads(serializers.serialize("json", NewModel.objects.all()))
            self._compare_old_new_data(old_data, new_data)

        # Check that old objects do not exist
        for model_name, _ in test_map.items():
            with self.test_case.assertRaises(
                LookupError, msg=f"{model_name} should no longer exist"
            ):
                new_state.apps.get_model(old_app_label, "model_name")

    def test_objects_do_not_exist(self, test_map, new_state, old_app_label):
        # Check that new objects do not exist after transfer
        for model_name, _ in test_map.items():
            with self.test_case.assertRaises(
                LookupError, msg=f"{model_name} should no longer exist"
            ):
                new_state.apps.get_model(old_app_label, "model_name")
