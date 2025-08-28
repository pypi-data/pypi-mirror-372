import copy
import logging
from typing import Union

from django.db.models import Model
from django.utils import timezone
from rest_framework.request import Request

from smoothglue.tracker.models import APIChangeLog

logger = logging.getLogger(__name__)


# pylint: disable=W0212
def create_change_log(request: Request, instance: Union[Model, None] = None) -> None:
    """
    Creates an APIChangeLog from a request
    """
    try:
        data = copy.deepcopy(request.data)
        if isinstance(data, dict) and instance:
            data.update(id=str(instance.id))

        APIChangeLog.objects.create(
            username=str(request.user)[:200],
            full_path=request._request.path[:200],
            method=request._request.method,
            timestamp=timezone.now(),
            data=data,
            params=request.query_params.dict(),
        )

    # Currently unsure what exceptions could occur, so using broad exception catch
    # pylint: disable=W0703
    except Exception as ex:
        logger.error(
            "Failed to log exception to db - %s: %s",
            type(ex).__name__,
            str(ex),
            exc_info=True,
        )
