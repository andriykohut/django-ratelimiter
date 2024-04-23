import abc
from typing import Callable, Optional

from django.http import HttpRequest, HttpResponse
from limits import parse
from limits.storage import Storage

from django_ratelimiter.utils import get_storage, get_rate_limiter


class AbstractRateLimiterMiddleware(abc.ABC):
    """Abstract base class for rate limiting middleware."""

    STRATEGY = "fixed-window"

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def storage_for(self, request: HttpRequest) -> Storage:
        """Override to set non-default storage."""
        return get_storage()

    def strategy_for(self, request: HttpRequest) -> str:
        """Override to customize strategy (i.e., based on a request path, method)"""
        return self.STRATEGY

    def keys_for(self, request: HttpRequest) -> list[str]:
        """By default, this will use middleware name for all requests,
        effectively this means global rate limiting for all requests.

        Override this method to rate-limit based on a request attribute like a path, user, etc.
        """
        return [f"{self.__class__.__module__}.{self.__class__.__qualname__}"]

    def ratelimit_response(self, request: HttpRequest) -> HttpResponse:
        """Override to return a custom response when rate limit is exceeded."""
        return HttpResponse("Too Many Requests", status=429)

    @abc.abstractmethod
    def rate_for(self, request: HttpRequest) -> Optional[str]:
        """Returns a rate for given request.

        If `None` is returned, request is not rate-limited.
        """

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if rate := self.rate_for(request):
            parsed_rate = parse(rate)
            keys = self.keys_for(request)
            strategy = self.strategy_for(request)
            storage = self.storage_for(request)
            rate_limiter = get_rate_limiter(strategy, storage)
            if not rate_limiter.hit(parsed_rate, *keys):
                return self.ratelimit_response(request)
        return self.get_response(request)
