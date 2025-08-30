import json
import logging

from django.db import connection


class ChangeLogHandler(logging.Handler):
    """
    Handles any changes to a model by the API.
    """

    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        msg = record.msg
        request = msg["request"]
        # Only record changes
        if request["method"] in ["POST", "PUT", "PATCH", "DELETE"]:
            username = "Unknown"
            if msg.get("user"):
                username = msg["user"].get("username", "Unknown")

            data = request["data"]
            if data:
                # Attempt to remove middlewaretoken
                parsed_data = json.loads(request["data"])
                parsed_data.pop("csrfmiddlewaretoken", None)
                data = json.dumps(parsed_data)
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO smoothglue_tracker_apichangelog (username, full_path,
                                                    method, timestamp,
                                                    data, params)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    [
                        str(username)[0:200],
                        str(request["full_path"])[0:200],
                        str(request["method"])[0:30],
                        msg["timestamp"],
                        str(data),
                        str(request["query_params"]),
                    ],
                )
