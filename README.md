# django-ratelimiter

[![PyPI version](https://badge.fury.io/py/django-ratelimiter.svg)](https://pypi.org/project/django-ratelimiter/)
[![CI](https://github.com/andriykohut/django-ratelimiter/actions/workflows/ci.yml/badge.svg)](https://github.com/andriykohut/django-ratelimiter/actions/workflows/ci.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/andriykohut/django-ratelimiter/branch/main/graph/badge.svg)](https://codecov.io/gh/andriykohut/django-ratelimiter)
[![Python Versions](https://img.shields.io/pypi/pyversions/django-ratelimiter)](https://pypi.python.org/pypi/django-ratelimiter/)
[![license](https://img.shields.io/pypi/l/django-ratelimiter.svg)](https://pypi.python.org/pypi/django-ratelimiter)
[![docs](https://readthedocs.org/projects/django-ratelimiter/badge/?version=latest)](https://django-ratelimiter.readthedocs.io/)

Rate limiting for django using [limits](https://limits.readthedocs.io/en/stable/).

Documentation: <https://django-ratelimiter.readthedocs.io>

## Installation

```py
pip install django-ratelimiter
```

## Usage

By default `django-ratelimiter` will use the default cache.

### Django configuration

To use a non-default cache define `DJANGO_RATELIMITER_CACHE` in `settings.py`.

```py
# Set up django caches
CACHES = {
    "custom-cache": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
    }
}

# "default" cache is used if setting is not defined.
DJANGO_RATELIMITER_CACHE = "custom-cache"
```

Any storage backend provided by `limits` package can also be used by defining `DJANGO_RATELIMITER_STORAGE`:

```py
from limits.storage import RedisStorage

DJANGO_RATELIMITER_STORAGE = RedisStorage(uri="redis://localhost:6379/0")
```

For more details on storages refer to limits [documentation](https://limits.readthedocs.io/en/stable/storage.html).

### Rate limiting strategies

- [Fixed window](https://limits.readthedocs.io/en/stable/strategies.html#fixed-window)
- [Fixed Window with Elastic Expiry](https://limits.readthedocs.io/en/stable/strategies.html#fixed-window-with-elastic-expiry)
- [Moving Window](https://limits.readthedocs.io/en/stable/strategies.html#moving-window) - Only supported with `limits` storage by setting `DJANGO_RATELIMITER_STORAGE`

### View decorator

By default all requests are rate limited

```py
from django_ratelimiter import ratelimit

@ratelimit("5/minute")
def view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("OK")
```

Pick a rate limiting strategy, default is `fixed-window`:

```py
# options: fixed-window, fixed-window-elastic-expiry, moving-window
@ratelimit("5/minute", strategy="fixed-window-elastic-expiry")
def view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("OK")
```

You can define per-user limits using request attribute key.

```py
@ratelimit("5/minute", key="user")
def view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("OK")
```

Callable key can be used to define more complex rules:

```py
@ratelimit("5/minute", key=lambda r: r.user.username)
def view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("OK")
```

Rate-limit only certain methods:

```py
@ratelimit("5/minute", methods=["POST", "PUT"])
def view(request):
    return HttpResponse("OK")
```

Provide a custom response:

```py
from django.http import HttpResponse

@ratelimit("5/minute", response=HttpResponse("Too many requests", status=400))
def view(request):
    return HttpResponse("OK")
```

Using non-default storage:

```py

from limits.storage import RedisStorage

@ratelimit("5/minute", storage=RedisStorage(uri="redis://localhost:6379/0"))
def view(request):
    return HttpResponse("OK")
```

### Middleware

Middleware can be used instead of decorators for more general cases.

```py
from typing import Optional

from django.http import HttpRequest

from django_ratelimiter.middleware import AbstractRateLimiterMiddleware


class RateLimiterMiddleware(AbstractRateLimiterMiddleware):
    def rate_for(self, request: HttpRequest) -> Optional[str]:
        # allow only 100 POST requests per minute
        if request.method == "POST":
            return "100/minute"
        # allow only 200 PUT requests per minute
        if request.methid == "PUT":
            return "200/minute"
        # all other requests are not rate limited
        return None
```

Middleware is customizable by overriding methods, see api reference for more details.

### DRF/ninja/class-based views

`django-ratelimiter` is framework-agnostic, it should work with DRF/ninja out of the box.
Class-based views are also supported with [method_decorator](https://docs.djangoproject.com/en/5.0/topics/class-based-views/intro/#decorating-the-class).

See examples in [test_app](./test_app/views.py).
