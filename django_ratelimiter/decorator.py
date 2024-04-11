from typing import Callable, Sequence
from functools import wraps, partial

from django.db import models
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from limits.strategies import STRATEGIES, RateLimiter
from limits.storage import Storage
from limits import parse
from django_ratelimiter.storage import CacheStorage
from django_ratelimiter.types import ViewFunc, P


def build_identifiers(
    func: ViewFunc, methods: str | Sequence[str] | None = None
) -> list[str]:
    if isinstance(func, partial):
        # method_decorator scenario
        identifiers = [
            func.func.__self__.__class__.__module__,
            f"{func.func.__self__.__class__.__qualname__}.{func.func.__name__}",
        ]
    else:
        identifiers = [func.__module__, func.__qualname__]
    if methods:
        methods_ = methods if isinstance(methods, str) else "|".join(sorted(methods))
        identifiers.append(methods_)
    return identifiers


def get_rate_limiter(strategy: str, storage: Storage | None = None) -> RateLimiter:
    if strategy not in STRATEGIES:
        raise ValueError(
            f"Unknown strategy {strategy}, must be one of {STRATEGIES.keys()}"
        )
    if not storage:
        default_storage = getattr(settings, "DJANGO_RATELIMITER_CACHE", None)
        storage = (
            default_storage if isinstance(default_storage, Storage) else CacheStorage()
        )
    return STRATEGIES[strategy](storage)


def ratelimit(
    rate: str | Callable[[HttpRequest], str],
    key: str | Callable[[HttpRequest], str] | None = None,
    methods: str | Sequence[str] | None = None,
    strategy: str = "fixed-window",
    response: HttpResponse | None = None,
    storage: Storage | None = None,
) -> Callable[[ViewFunc], ViewFunc]:
    rate_limiter = get_rate_limiter(strategy, storage)

    def decorator(func: ViewFunc) -> ViewFunc:
        @wraps(func)
        def wrapper(
            request: HttpRequest, *args: P.args, **kwargs: P.kwargs
        ) -> HttpResponse:
            rate_str = rate(request) if callable(rate) else rate
            parsed_rate = parse(rate_str)
            if getattr(settings, "DJANGO_RATELIMITER_CACHE", True) and (
                not methods or request.method in methods
            ):
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
