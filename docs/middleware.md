# Middleware

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

Middleware is customizable by overriding methods, see [api reference](/api_reference/#django_ratelimiter.middleware.AbstractRateLimiterMiddleware) for more details.
