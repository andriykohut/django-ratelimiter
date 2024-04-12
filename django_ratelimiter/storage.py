import time
from typing import Union, Optional

from django.core.cache import caches, BaseCache

from limits.storage import Storage


class CacheStorage(Storage):

    def __init__(
        self,
        cache: str,
        wrap_exceptions: bool = False,
        **options: Union[float, str, bool],
    ) -> None:
        self.cache: BaseCache = caches[cache]
        super().__init__(uri=None, wrap_exceptions=wrap_exceptions, **options)

    @property
    def base_exceptions(self) -> Union[type[Exception], tuple[type[Exception], ...]]:
        return Exception

    def get(self, key: str) -> int:
        return self.cache.get(key, 0)

    def incr(
        self, key: str, expiry: int, elastic_expiry: bool = False, amount: int = 1
    ) -> int:
        self.cache.get_or_set(key, 0, expiry)
        self.cache.get_or_set(f"{key}/expires", time.time() + expiry, expiry)
        try:
            value = self.cache.incr(key, amount) or amount
        except ValueError:
            value = amount
        if elastic_expiry:
            self.cache.touch(key, expiry)
            self.cache.set(f"{key}/expires", time.time() + expiry, expiry)
        return value

    def get_expiry(self, key: str) -> int:
        return int(float(self.cache.get(key + "/expires") or time.time()))

    def check(self) -> bool:
        try:
            self.cache.get("django-ratelimiter-check")
            return True
        except:  # noqa: E722
            return False

    def reset(self) -> Optional[int]:
        raise NotImplementedError

    def clear(self, key: str) -> None:
        self.cache.delete(key)
