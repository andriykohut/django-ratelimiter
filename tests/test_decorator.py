from datetime import datetime

import freezegun
import pytest
from django.http import HttpResponse
from django.test import RequestFactory
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views import View
from limits import parse
from limits.storage import MemoryStorage, RedisStorage, MemcachedStorage

from django_ratelimiter import ratelimit
from django_ratelimiter.decorator import get_rate_limiter


@pytest.fixture
def fixed_window():
    return get_rate_limiter("fixed-window")


@pytest.fixture(autouse=True, scope="function")
def clear_cache():
    cache.clear()


@freezegun.freeze_time(datetime.now(), auto_tick_seconds=1)
def test_defaults(fixed_window):
    rate_str = "5/minute"
    rate = parse(rate_str)

    @ratelimit(rate_str)
    def view(_):
        return HttpResponse("OK")

    request = RequestFactory().get("/")

    initial_stats = None

    for i in reversed(range(5)):
        response = view(request)
        assert response.status_code == 200
        stats = fixed_window.get_window_stats(rate, view.__module__, view.__qualname__)
        if initial_stats is None:
            initial_stats = stats
        assert stats.remaining == i
        assert stats.reset_time == initial_stats.reset_time

    response = view(request)
    assert response.status_code == 429
    stats = fixed_window.get_window_stats(rate, view.__module__, view.__qualname__)
    assert stats.reset_time == initial_stats.reset_time


def test_key_string(fixed_window):
    from django.contrib.auth.models import User

    rate_str = "5/minute"
    rate = parse(rate_str)

    @ratelimit(rate_str, key="user")
    def view(_):
        return HttpResponse("OK")

    request = RequestFactory().get("/")
    request.user = User(pk=13)
    stats = fixed_window.get_window_stats(
        rate, view.__module__, view.__qualname__, request.user.pk
    )
    assert stats.remaining == 5

    for _ in range(5):
        response = view(request)
        assert response.status_code == 200

    response = view(request)
    assert response.status_code == 429
    stats = fixed_window.get_window_stats(
        rate, view.__module__, view.__qualname__, request.user.pk
    )
    assert stats.remaining == 0

    request = RequestFactory().get("/")
    request.user = User(pk=14)
    response = view(request)
    assert response.status_code == 200
    assert (
        ":1:LIMITER/test_decorator/test_key_string.<locals>.view/14/5/1/minute"
        in cache._cache
    )
    stats = fixed_window.get_window_stats(
        rate, view.__module__, view.__qualname__, request.user.pk
    )
    assert stats.remaining == 4


def test_key_function():
    from django.contrib.auth.models import User

    @ratelimit("5/minute", key=lambda r: r.user.username)
    def view(_):
        return HttpResponse("OK")

    request = RequestFactory().get("/")
    request.user = User(pk=13, username="a")

    for _ in range(5):
        response = view(request)
        assert response.status_code == 200

    response = view(request)
    assert response.status_code == 429

    request = RequestFactory().get("/")
    request.user = User(pk=14, username="b")
    response = view(request)
    assert response.status_code == 200


def test_methods():
    @ratelimit("5/minute", methods=["POST", "PUT"])
    def view(_):
        return HttpResponse("OK")

    request = RequestFactory().get("/")
    for _ in range(6):
        response = view(request)
        assert response.status_code == 200

    assert not cache._cache

    request = RequestFactory().post("/")
    for _ in range(5):
        response = view(request)
        assert response.status_code == 200
    response = view(request)
    assert response.status_code == 429
    request = RequestFactory().put("/")
    response = view(request)
    assert response.status_code == 429
    request = RequestFactory().get("/")
    response = view(request)
    assert response.status_code == 200


@freezegun.freeze_time(datetime.now(), auto_tick_seconds=1)
def test_fixed_window_with_elastic_expiry():
    request = RequestFactory().get("/")

    rate_limiter = get_rate_limiter("fixed-window-elastic-expiry")

    @ratelimit("5/minute", strategy="fixed-window-elastic-expiry")
    def view(_):
        return HttpResponse("OK")

    item = parse("5/minute")

    for i in range(5):
        response = view(request)
        assert response.status_code == 200
        stats = rate_limiter.get_window_stats(item, view.__module__, view.__qualname__)
        assert stats.remaining == 5 - (i + 1)

    response = view(request)
    assert response.status_code == 429
    new_stats = rate_limiter.get_window_stats(item, view.__module__, view.__qualname__)
    assert new_stats.remaining == 0
    assert new_stats.reset_time > stats.reset_time


def test_custom_response():
    request = RequestFactory().get("/")

    @ratelimit("1/minute", response=HttpResponse(status=400))
    def view(_):
        return HttpResponse("OK")

    response = view(request)
    assert response.status_code == 200

    response = view(request)
    assert response.status_code == 400


def test_cvb():
    @method_decorator(ratelimit("1/minute"), name="dispatch")
    class ViewA(View):
        def get(self, _):
            return HttpResponse("OK")

        def post(self, _):
            return HttpResponse("OK")

    request = RequestFactory().get("/")
    response = ViewA.as_view()(request)
    assert response.status_code == 200

    response = ViewA.as_view()(request)
    assert response.status_code == 429

    class ViewB(View):
        @ratelimit("1/minute")
        def get(self, _):
            return HttpResponse("OK")

    response = ViewB.as_view()(request)
    assert response.status_code == 200

    response = ViewB.as_view()(request)
    assert response.status_code == 429


@pytest.mark.parametrize(
    "storage",
    [
        MemoryStorage(),
        RedisStorage(uri="redis://localhost:6379/0"),
        MemcachedStorage(uri="memcached://localhost:11211"),
    ],
)
def test_limits_storage(storage):
    rate_str = "5/minute"
    rate = parse(rate_str)

    @ratelimit(rate_str, storage=storage)
    def view(_):
        return HttpResponse("OK")

    storage.clear(rate.key_for(view.__module__, view.__qualname__))

    request = RequestFactory().get("/")

    for _ in range(5):
        response = view(request)
        assert response.status_code == 200

    response = view(request)
    assert response.status_code == 429
