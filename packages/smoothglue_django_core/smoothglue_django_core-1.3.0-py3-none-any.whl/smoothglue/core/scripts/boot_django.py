"""
This file sets up and configures Django.
It's used by scripts that need to execute as if running in a Django server.
"""

import django
from django.conf import settings

from smoothglue.core.scripts import test_settings


def boot_django():
    # The settings.configure() call takes a list of args that are equivalent
    # to variables defined in a test_settings.py file.
    # Anything you would need in your test_settings.py to make your app run gets passed here
    settings.configure(
        BASE_DIR=test_settings.BASE_DIR,
        DEBUG=test_settings.DEBUG,
        DATABASES=test_settings.DATABASES,
        INSTALLED_APPS=test_settings.INSTALLED_APPS,
        TIME_ZONE=test_settings.TIME_ZONE,
        USE_TZ=test_settings.USE_TZ,
        ROOT_URLCONF=test_settings.ROOT_URLCONF,
        AUTH_USER_MODEL=test_settings.AUTH_USER_MODEL,
        SECRET_KEY=test_settings.SECRET_KEY,
        REMOTE_USER_HEADER=test_settings.REMOTE_USER_HEADER,
    )
    django.setup()
