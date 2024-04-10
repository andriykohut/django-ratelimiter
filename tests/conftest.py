import django
from django.conf import settings
from django.core import management

import pytest

from django_limits.types import ViewFunc


@pytest.fixture(scope="session", autouse=True)
def configure_settings():
    settings.configure(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "unique-snowflake",
            },
            "locmem": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "unique-snowflake",
            },
            "memcached": {
                "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
                "LOCATION": "127.0.0.1:11211",
            },
            "filebased": {
                "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
                "LOCATION": "/var/tmp/django_cache",
            },
            "redis": {
                "BACKEND": "django.core.cache.backends.redis.RedisCache",
                "LOCATION": "redis://127.0.0.1:6379",
            },
            "db": {
                "BACKEND": "django.core.cache.backends.db.DatabaseCache",
                "LOCATION": "cache",
            },
        },
        DATABASES={
            "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
        },
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
        ],
    )
    django.setup()
    management.call_command("createcachetable")
