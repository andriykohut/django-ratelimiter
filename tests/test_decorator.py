from datetime import datetime

import freezegun
import pytest
from django.core.cache import cache
from limits import parse

from django_ratelimiter.decorator import get_rate_limiter
from test_app import views
from tests.utils import wait_for_rate_limit

TEST_RATE = parse("5/minute")


@pytest.fixture
def fixed_window():
    return get_rate_limiter("fixed-window")


@pytest.fixture(autouse=True, scope="function")
def clear_cache():
    cache.clear()


@freezegun.freeze_time(datetime.now(), auto_tick_seconds=1)
def test_defaults(client, fixed_window):
    identifiers = views.defaults.__module__, views.defaults.__qualname__
    initial_stats = None

    for i in reversed(range(5)):
        response = client.get(f"/defaults/{i}/")
        assert response.status_code == 200
        stats = fixed_window.get_window_stats(TEST_RATE, *identifiers)
        if initial_stats is None:
            initial_stats = stats
        assert stats.remaining == i
        assert stats.reset_time == initial_stats.reset_time

    response = client.get("/defaults/7/")
    assert response.status_code == 429
    stats = fixed_window.get_window_stats(TEST_RATE, *identifiers)
    assert stats.reset_time == initial_stats.reset_time


def test_key_string(fixed_window, client, django_user_model):
    user1 = django_user_model.objects.create_user(
        username="user1", password="password1"
    )
    user2 = django_user_model.objects.create_user(
        username="user2", password="password2"
    )
    identifiers = views.by_string_key.__module__, views.by_string_key.__qualname__
    stats = fixed_window.get_window_stats(TEST_RATE, *identifiers, user1.pk)
    assert stats.remaining == 5

    client.force_login(user1)

    for _ in range(5):
        response = client.get("/by-string-key/")
        assert response.status_code == 200

    response = client.get("/by-string-key/")
    assert response.status_code == 429
    stats = fixed_window.get_window_stats(TEST_RATE, *identifiers, user1.pk)
    assert stats.remaining == 0

    client.force_login(user2)

    response = client.get("/by-string-key/")
    assert response.status_code == 200
    assert (
        f":1:LIMITER/test_app.views/by_string_key/{user1.pk}/5/1/minute" in cache._cache
    )
    stats = fixed_window.get_window_stats(TEST_RATE, *identifiers, user2.pk)
    assert stats.remaining == 4


def test_key_function(django_user_model, client, fixed_window):
    user1 = django_user_model.objects.create_user(
        username="user1", password="password1"
    )
    user2 = django_user_model.objects.create_user(
        username="user2", password="password2"
    )
    identifiers = views.by_string_key.__module__, views.by_string_key.__qualname__
    stats = fixed_window.get_window_stats(TEST_RATE, *identifiers, user1.pk)
    assert stats.remaining == 5

    client.force_login(user1)

    assert wait_for_rate_limit("/by-func-key/", client=client) == 5

    response = client.get("/by-func-key/")
    assert response.status_code == 429

    client.force_login(user2)

    response = client.get("/by-func-key/")
    assert response.status_code == 200


def test_methods(client):
    for _ in range(6):
        response = client.get("/by-method/")
        assert response.status_code == 200

    assert not cache._cache

    assert wait_for_rate_limit("/by-method/", method="POST") == 5

    response = client.post("/by-method/")
    assert response.status_code == 429

    response = client.put("/by-method/")
    assert response.status_code == 429

    response = client.get("/by-method/")
    assert response.status_code == 200


@freezegun.freeze_time(datetime.now(), auto_tick_seconds=1)
def test_fixed_window_with_elastic_expiry(client):
    rate_limiter = get_rate_limiter("fixed-window-elastic-expiry")
    identifiers = (
        views.fixed_window_elastic_expiry.__module__,
        views.fixed_window_elastic_expiry.__qualname__,
    )

    for i in range(5):
        response = client.get("/fixed-window-elastic-expiry/")
        assert response.status_code == 200
        stats = rate_limiter.get_window_stats(TEST_RATE, *identifiers)
        assert stats.remaining == 5 - (i + 1)

    response = client.get("/fixed-window-elastic-expiry/")
    assert response.status_code == 429
    new_stats = rate_limiter.get_window_stats(TEST_RATE, *identifiers)
    assert new_stats.remaining == 0
    assert new_stats.reset_time > stats.reset_time


def test_custom_response(client):
    response = client.get("/teapot/")
    assert response.status_code == 200

    response = client.get("/teapot/")
    assert response.status_code == 418


def test_cbv(client):
    response = client.get("/cbv/")
    assert response.status_code == 200

    response = client.get("/cbv/")
    assert response.status_code == 429


@pytest.mark.parametrize(
    "path, storage, view",
    (
        ("memory", views.memory_storage, views.memory),
        ("redis", views.redis_storage, views.redis),
        ("memcached", views.memcached_storage, views.memcached),
    ),
)
def test_limits_storage(path, storage, view):
    storage.clear(TEST_RATE.key_for(view.__module__, view.__qualname__))
    assert wait_for_rate_limit(f"/storage/{path}/") == 5


@pytest.mark.parametrize(
    "url",
    [
        "/drf/api-view/",
        "/drf/view/",
        "/drf/viewset/",
    ],
)
@pytest.mark.django_db
def test_drf(url, drf_client):
    assert wait_for_rate_limit(url, client=drf_client) == 5
