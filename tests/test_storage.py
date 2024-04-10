import time

import uuid
import pytest

from django_limits.storage import CacheStorage


@pytest.mark.parametrize(
    "cache",
    [
        "locmem",
        "memcached",
        "filebased",
        "redis",
        "db",
    ],
)
def test_storage(cache):
    key = str(uuid.uuid4())
    storage = CacheStorage(cache)
    # Key does not exist
    assert storage.get(key) == 0
    assert storage.get_expiry(key) <= time.time()
    storage.clear(key)

    assert storage.incr(key, 3) == 1

    # expiry was set during increment
    initial_expiry = storage.get_expiry(key)

    # add amount and change expiry
    assert storage.incr(key, 5, amount=2) == 3
    # expiry didn't change after increment
    assert storage.get_expiry(key) == initial_expiry

    # elastic expiry updates expiry on increment
    assert storage.incr(key, 4, elastic_expiry=True) == 4
    assert storage.get_expiry(key) != initial_expiry

    # get works
    assert storage.get(key) == 4

    # clear removes value from cache
    storage.clear(key)
    assert storage.get(key) == 0

    # negative expiry
    assert storage.incr("auto-remove", -1) == 1
    assert storage.get("auto-remove") == 0
