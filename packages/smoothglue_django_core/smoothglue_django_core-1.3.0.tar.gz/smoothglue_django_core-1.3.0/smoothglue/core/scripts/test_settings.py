"""
This is required to be a separate module for pylint.
Since pylint isn't able to utilize the boot_django utility a "real" django settings module is
required.
"""

import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "smoothglue"))
DEBUG = True
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.auth",
    "smoothglue.core",
    "smoothglue.tracker",
    "smoothglue.authentication",
]
TIME_ZONE = "UTC"
USE_TZ = True
ROOT_URLCONF = "smoothglue.authentication.urls"
AUTH_USER_MODEL = "authentication.PlatformUser"
SECRET_KEY = "TEST"
REMOTE_USER_HEADER = "HTTP_X_USERNAME"
