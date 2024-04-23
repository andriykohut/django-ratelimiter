from typing import Callable, Literal, Sequence, Union, Optional
from functools import wraps

from django.db import models
from django.http import HttpRequest, HttpResponse
from limits.storage import Storage
from limits import parse
from django_ratelimiter.types import ViewFunc, P
from django_ratelimiter.utils import build_identifiers, get_rate_limiter


def ratelimit(
    rate: Union[str, Callable[[HttpRequest], str]],
    key: Union[str, Callable[[HttpRequest], str], None] = None,
    methods: Union[str, Sequence[str], None] = None,
    strategy: Literal[
        "fixed-window",
        "fixed-window-elastic-expiry",
        "moving-window",
    ] = "fixed-window",
    response: Optional[HttpResponse] = None,
    storage: Optional[Storage] = None,
    cache: Optional[str] = None,
) -> Callable[[ViewFunc], ViewFunc]:
    """Rate limiting decorator for wrapping views.

    Arguments:
        rate: rate string (i.e. `5/second`) or a callable that takes a request and returns a rate
        key: request attribute or callable that returns a string to be used as identifier
        methods: only rate limit specified method(s)
        strategy: a name of rate limiting strategy
        response: custom rate limit response instance
        storage: override default rate limit storage
        cache: override default cache name if using django cache storage backend
    """
    if storage and cache:
        raise ValueError("Can't use both cache and storage")
    rate_limiter = get_rate_limiter(strategy, storage)

    def decorator(func: ViewFunc) -> ViewFunc:
        @wraps(func)
        def wrapper(
            request: HttpRequest, *args: P.args, **kwargs: P.kwargs
        ) -> HttpResponse:
            rate_str = rate(request) if callable(rate) else rate
            parsed_rate = parse(rate_str)
            if not methods or request.method in methods:
                identifiers = build_identifiers(func, methods)
                if key:
                    value = key(request) if callable(key) else getattr(request, key)
                    value = str(value.pk if isinstance(value, models.Model) else value)
                    identifiers.append(value)

                if not rate_limiter.hit(parsed_rate, *identifiers):
                    return response or HttpResponse(
                        "Too Many Requests",
                        status=429,
                    )
            return func(request, *args, **kwargs)

        return wrapper

    return decorator
