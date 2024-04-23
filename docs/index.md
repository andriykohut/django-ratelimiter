<p align="center">
    <em>Rate limiting for django using <a href="https://limits.readthedocs.io/en/stable/">limits</a>.</em>
</p>

---

Documentation: <https://andriykohut.github.io/django-ratelimiter/>

Sources: <https://github.com/andriykohut/django-ratelimiter>

---

Django ratelimiter provides a decorator to wrap Django views. It relies on [limits](https://limits.readthedocs.io/en/stable/) library.

By default it uses it's own storage backend based on django cache, but it can also use [storages provided by limits](https://limits.readthedocs.io/en/stable/storage.html).

## Quickstart

### Django configuration

With django cache storage:

```py
# Set up django caches
CACHES = {
    "redis": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
    }
}

# "default" cache is used if setting is not defined.
DJANGO_RATELIMITER_CACHE = "redis"
```

With `limits` storage:

```py
from limits.storage import RedisStorage

DJANGO_RATELIMITER_STORAGE = RedisStorage(uri="redis://localhost:6379/0")
```

### Decorate the view

```py
from django_ratelimiter import ratelimit

@ratelimit("5/minute")
def view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("OK")
```

See [more examples](decorator.md).
