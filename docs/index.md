<p align="center">
    <em>Rate limiting for django using <a href="https://limits.readthedocs.io/en/stable/">limits</a>.</em>
</p>

---

Documentation: <https://django-ratelimiter.readthedocs.io>

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

### View decorator

By default all requests are rate limited

```py
from django_ratelimiter import ratelimit

@ratelimit("5/minute")
def view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("OK")
```

Per-user limits (using request attribute key)

```py
@ratelimit("5/minute", key="user")
def view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("OK")
```

Callable key can be used to define more complex rules

```py
@ratelimit("5/minute", key=lambda r: r.user.username)
def view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("OK")
```

Define which HTTP methods to rate limit

```py
@ratelimit("5/minute", methods=["POST", "PUT"])
def view(request):
    return HttpResponse("OK")
```

Custom response:

```py
from django.http import HttpResponse

@ratelimit("5/minute", response=HttpResponse("Too many requests", status=400))
def view(request):
    return HttpResponse("OK")
```

Per-view storage:

```py

from limits.storage import RedisStorage

@ratelimit("5/minute", storage=RedisStorage(uri="redis://localhost:6379/0"))
def view(request):
    return HttpResponse("OK")
```
