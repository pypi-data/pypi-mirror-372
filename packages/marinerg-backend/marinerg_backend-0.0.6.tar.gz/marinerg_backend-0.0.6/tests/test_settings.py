from pathlib import Path
import os

SECRET_KEY = "fake-key"

MEDIA_ROOT = Path(__file__).parent / "test_output/mediafiles/"
os.makedirs(MEDIA_ROOT, exist_ok=True)

INSTALLED_APPS = [
    "tests",
    "api",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "rest_framework.authtoken",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db.sqlite3",
        "USER": "user",
        "PASSWORD": "password",
    }
}

ROOT_URLCONF = "api.urls"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
}
