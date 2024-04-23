from functools import partial, lru_cache
from typing import Union, Sequence, Optional

from django.conf import settings
from limits.storage import Storage
from limits.strategies import STRATEGIES, RateLimiter

from django_ratelimiter.storage import CacheStorage
from django_ratelimiter.types import ViewFunc


def build_identifiers(
    func: ViewFunc, methods: Union[str, Sequence[str], None] = None
) -> list[str]:
    """Build view identifiers for storage cache key using function signature and list of methods."""
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


@lru_cache(maxsize=None)
def get_storage() -> Storage:
    """Returns a default storage backend instance, defined by either `DJANGO_RATELIMITER_CACHE`
    or `DJANGO_RATELIMITER_STORAGE`."""
    cache_name: Optional[str] = getattr(settings, "DJANGO_RATELIMITER_CACHE", None)
    storage: Optional[Storage] = getattr(settings, "DJANGO_RATELIMITER_STORAGE", None)
    if cache_name and storage:
        raise ValueError(
            "DJANGO_RATELIMITER_CACHE and DJANGO_RATELIMITER_STORAGE can't be used together"
        )
    return storage or CacheStorage(cache_name or "default")


def get_rate_limiter(strategy: str, storage: Optional[Storage] = None) -> RateLimiter:
    """Return a ratelimiter instance for given strategy."""
    if strategy not in STRATEGIES:
        raise ValueError(
            f"Unknown strategy {strategy}, must be one of {STRATEGIES.keys()}"
        )
    storage = storage or get_storage()
    return STRATEGIES[strategy](storage)
