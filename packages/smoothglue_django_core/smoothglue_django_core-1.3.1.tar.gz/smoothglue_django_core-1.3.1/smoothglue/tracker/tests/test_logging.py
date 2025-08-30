import json
import logging
import unittest
from unittest.mock import patch

from smoothglue.tracker.logging import ChangeLogHandler


class TestChangeLogHandler(unittest.TestCase):
    def setUp(self):
        self.handler = ChangeLogHandler()
        self.mock_record = logging.LogRecord(
            name="test-logger",
            level=logging.INFO,
            pathname="test_pathname",
            lineno=1,
            msg={},
            args=(),
            exc_info=None,
            func="test_func",
        )

    def _prepare_record_msg(
        self, method, user, data, full_path, query_params, timestamp
    ):
        """Helper to construct the msg dictionary for the log record."""
        self.mock_record.msg = {
            "request": {
                "method": method,
                "data": data,
                "full_path": full_path,
                "query_params": query_params,
            },
            "user": user,
            "timestamp": timestamp,
        }

    @patch("smoothglue.tracker.logging.connection")
    def test_emit_non_change_method_does_not_log(self, mock_connection):
        """Test that methods like GET don't result in a database write."""
        mock_cursor = mock_connection.cursor.return_value.__enter__.return_value

        self._prepare_record_msg(
            method="GET",
            user={"username": "testuser"},
            data=None,
            full_path="/api/items",
            query_params="{}",
            timestamp="2023-10-27T10:00:00Z",
        )
        self.handler.emit(self.mock_record)
        mock_cursor.execute.assert_not_called()

    @patch("smoothglue.tracker.logging.connection")
    def test_emit_post_request_with_user_and_data(self, mock_connection):
        """Test a POST request with user and data, including CSRF token removal."""
        mock_cursor = mock_connection.cursor.return_value.__enter__.return_value
        timestamp = "2023-10-27T10:00:00Z"
        original_data_dict = {"key": "value", "csrfmiddlewaretoken": "testtoken"}
        original_data_json = json.dumps(original_data_dict)
        expected_data_json = json.dumps({"key": "value"})
        username = "testuser"
        full_path = "/api/resource"
        query_params_str = "{'param': 'value'}"

        self._prepare_record_msg(
            method="POST",
            user={"username": username},
            data=original_data_json,
            full_path=full_path,
            query_params=query_params_str,
            timestamp=timestamp,
        )
        self.handler.emit(self.mock_record)

        expected_sql = """
                    INSERT INTO smoothglue_tracker_apichangelog (username, full_path,
                                                    method, timestamp,
                                                    data, params)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
        expected_params = [
            username,
            full_path,
            "POST",
            timestamp,
            expected_data_json,
            query_params_str,
        ]
        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args[0]
        self.assertEqual(" ".join(expected_sql.split()), " ".join(call_args[0].split()))
        self.assertEqual(expected_params, call_args[1])

    @patch("smoothglue.tracker.logging.connection")
    def test_emit_put_request_anonymous_user_no_data(self, mock_connection):
        """Test a PUT request with an anonymous user and no data."""
        mock_cursor = mock_connection.cursor.return_value.__enter__.return_value
        timestamp = "2023-10-27T10:05:00Z"
        full_path = "/api/resource/1"
        query_params_str = "{}"

        self._prepare_record_msg(
            method="PUT",
            user=None,  # Anonymous user
            data=None,  # No data
            full_path=full_path,
            query_params=query_params_str,
            timestamp=timestamp,
        )
        self.handler.emit(self.mock_record)

        expected_params = [
            "Unknown",
            full_path,
            "PUT",
            timestamp,
            "None",
            query_params_str,
        ]
        mock_cursor.execute.assert_called_once()
        self.assertEqual(expected_params, mock_cursor.execute.call_args[0][1])

    @patch("smoothglue.tracker.logging.connection")
    def test_emit_delete_request_data_without_csrf_token(self, mock_connection):
        """Test DELETE with data that doesn't contain a CSRF token."""
        mock_cursor = mock_connection.cursor.return_value.__enter__.return_value
        timestamp = "2023-10-27T10:10:00Z"
        data_dict = {"id": 123, "force": True}
        data_json = json.dumps(data_dict)
        username = "deleter_user"
        full_path = "/api/items/123"
        query_params_str = "{'hard_delete': 'true'}"

        self._prepare_record_msg(
            method="DELETE",
            user={"username": username},
            data=data_json,
            full_path=full_path,
            query_params=query_params_str,
            timestamp=timestamp,
        )
        self.handler.emit(self.mock_record)

        expected_params = [
            username,
            full_path,
            "DELETE",
            timestamp,
            data_json,
            query_params_str,
        ]
        mock_cursor.execute.assert_called_once()
        self.assertEqual(expected_params, mock_cursor.execute.call_args[0][1])

    @patch("smoothglue.tracker.logging.connection")
    def test_emit_patch_request_empty_json_object_data(self, mock_connection):
        """Test PATCH with data being an empty JSON object string '{}'."""
        mock_cursor = mock_connection.cursor.return_value.__enter__.return_value
        timestamp = "2023-10-27T10:15:00Z"
        empty_json_data_str = "{}"
        username = "patch_user_empty_json"
        full_path = "/api/config/def"
        query_params_str = "{}"

        self._prepare_record_msg(
            method="PATCH",
            user={"username": username},
            data=empty_json_data_str,
            full_path=full_path,
            query_params=query_params_str,
            timestamp=timestamp,
        )
        self.handler.emit(self.mock_record)

        expected_params = [
            username,
            full_path,
            "PATCH",
            timestamp,
            empty_json_data_str,
            query_params_str,
        ]
        mock_cursor.execute.assert_called_once()
        self.assertEqual(expected_params, mock_cursor.execute.call_args[0][1])

    @patch("smoothglue.tracker.logging.connection")
    def test_emit_data_truncation(self, mock_connection):
        """Test that username and full_path are truncated if too long."""
        mock_cursor = mock_connection.cursor.return_value.__enter__.return_value
        timestamp = "2023-10-27T10:20:00Z"
        long_username = "u" * 250
        long_full_path = "/a/b/c/" * 100
        method = "POST"

        self._prepare_record_msg(
            method=method,
            user={"username": long_username},
            data=None,
            full_path=long_full_path,
            query_params="{}",
            timestamp=timestamp,
        )
        self.handler.emit(self.mock_record)

        expected_params = [
            long_username[:200],
            long_full_path[:200],
            method,
            timestamp,
            "None",
            "{}",
        ]
        mock_cursor.execute.assert_called_once()
        actual_params = mock_cursor.execute.call_args[0][1]

        self.assertEqual(expected_params[0], actual_params[0])
        self.assertEqual(len(actual_params[0]), 200)
        self.assertEqual(expected_params[1], actual_params[1])
        self.assertEqual(len(actual_params[1]), 200)
        self.assertEqual(expected_params[2:], actual_params[2:])

    @patch("smoothglue.tracker.logging.connection")
    def test_emit_user_is_none(self, mock_connection):
        """Test when msg['user'] itself is None, not just missing 'username'."""
        mock_cursor = mock_connection.cursor.return_value.__enter__.return_value
        timestamp = "2023-10-27T10:25:00Z"

        self._prepare_record_msg(
            method="POST",
            user=None,
            data='{"key": "value"}',
            full_path="/api/somepath",
            query_params="{}",
            timestamp=timestamp,
        )
        self.handler.emit(self.mock_record)

        expected_params_subset = [
            "Unknown",
            "/api/somepath",
            "POST",
            timestamp,
            '{"key": "value"}',
            "{}",
        ]
        mock_cursor.execute.assert_called_once()
        self.assertEqual(expected_params_subset, mock_cursor.execute.call_args[0][1])

    @patch("smoothglue.tracker.logging.connection")
    def test_emit_user_dict_empty_or_no_username(self, mock_connection):
        """Test when msg['user'] is a dict but empty or lacks 'username' key."""
        mock_cursor = mock_connection.cursor.return_value.__enter__.return_value
        timestamp = "2023-10-27T10:30:00Z"

        self._prepare_record_msg(
            method="PUT",
            user={},
            data=None,
            full_path="/api/path1",
            query_params="{}",
            timestamp=timestamp,
        )
        self.handler.emit(self.mock_record)
        mock_cursor.execute.assert_called_once()
        self.assertEqual("Unknown", mock_cursor.execute.call_args[0][1][0])
        mock_cursor.reset_mock()

        self._prepare_record_msg(
            method="PATCH",
            user={"id": 1, "email": "user@example.com"},
            data=None,
            full_path="/api/path2",
            query_params="{}",
            timestamp=timestamp,
        )
        self.handler.emit(self.mock_record)
        mock_cursor.execute.assert_called_once()
        self.assertEqual("Unknown", mock_cursor.execute.call_args[0][1][0])
