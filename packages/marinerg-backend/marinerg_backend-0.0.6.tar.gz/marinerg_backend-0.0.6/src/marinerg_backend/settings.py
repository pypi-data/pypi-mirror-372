"""
Django settings
"""

from pathlib import Path

from ichec_django_core import settings
from ichec_django_core.settings import *

BASE_DIR = Path(__file__).resolve().parent.parent

ROOT_URLCONF = "app.urls"
WSGI_APPLICATION = "app.wsgi.application"
ASGI_APPLICATION = "app.asgi.application"

TEMPLATES = settings.get_templates(BASE_DIR)
DATABASES = settings.get_databases(BASE_DIR)

STATIC_ROOT = settings.get_static_root(BASE_DIR)
MEDIA_ROOT = settings.get_media_root(BASE_DIR)

INSTALLED_APPS = [
    "marinerg_test_access.apps.MarinergTestAccessConfig",
    "marinerg_data_access.apps.MarinergDataAccessConfig",
    "marinerg_facility.apps.MarinergFacilityConfig",
]
INSTALLED_APPS.extend(settings.INSTALLED_APPS)

