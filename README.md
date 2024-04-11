# django-ratelimiter

TBD

## Synopsis

```py
from django.http import HttpRequest, HttpResponse
from django_ratelimiter import ratelimit
from limits.storage import RedisStorage

# defaults, limit all requests
@ratelimit("5/minute")
def view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("OK")

# limit per-user (request attribute key)
@ratelimit("5/minute", key="user")
def view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("OK")

# custom key function
@ratelimit("5/minute", key=lambda r: r.user.username)
def view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("OK")

# limit only specific methods
@ratelimit("5/minute", methods=["POST", "PUT"])
def view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("OK")

# custom response
@ratelimit("5/minute", response=HttpResponse("Too many requests", status=400))
def view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("OK")

# Using `limits.storage` storages
@ratelimit("5/minute", storage=RedisStorage(uri="redis://localhost:6379/0"))
def view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("OK")
```
