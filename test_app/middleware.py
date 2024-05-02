from typing import Optional

from django.http import HttpRequest
from django.urls import Resolver404, resolve

from django_ratelimiter.middleware import AbstractRateLimiterMiddleware


class RateLimiterMiddleware(AbstractRateLimiterMiddleware):
    def rate_for(self, request: HttpRequest) -> Optional[str]:
        match = None
        try:
            match = resolve(request.path_info)
        except Resolver404:
            pass
        # only ratelimit /test-middleware/hit/ requests
        if (
            match
            and match.url_name == "test_middleware"
            and match.kwargs["kind"] == "hit"
        ):
            return "3/minute"
        return None
