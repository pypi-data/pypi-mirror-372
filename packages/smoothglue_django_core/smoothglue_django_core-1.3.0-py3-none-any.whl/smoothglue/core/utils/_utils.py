from typing import Any, Dict, List

from django.conf import settings


def check_kwargs(list_keywords: List[str], kwargs: Dict[str, Any]) -> None:
    """
    Check if the provided keywords exist in the kwargs dictionary.

    This function iterates over each keyword in the list_keywords and asserts
    if each keyword exists as a key in the kwargs dictionary. An assertion error
    is raised if a keyword is not found as a key in the kwargs.

    Parameters:
    - list_keywords : List[str]
        A list of keywords to be checked in the kwargs.

    - kwargs : Dict[str, Any]
        A dictionary of keyword arguments in which the keywords
        from list_keywords will be checked.

    Returns:
    - None

    Raises:
    - AssertionError:
        If a keyword from list_keywords is not found as a key in kwargs.
    """

    for keyword in list_keywords:
        assert (
            keyword in kwargs
        ), f"{keyword} does not exist in kwargs keys:\n{list(kwargs.keys())}"


def get_setting(name, app_defaults):
    """
    Retrieves a setting value from the Django project's settings, falling back to the app's
    default settings if the setting is not found in the project's settings.

    Parameters:
    name (str): The name of the setting.
    app_defaults (module): The defaults module of the app where default settings are defined.

    Returns:
    The value of the setting from the project's settings or the app's default settings.
    """
    return getattr(settings, name, getattr(app_defaults, name))
