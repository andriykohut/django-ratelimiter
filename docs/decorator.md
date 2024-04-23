# View decorator

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
