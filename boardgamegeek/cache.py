import requests
import requests_cache
from requests_cache import SQLiteCache, DynamoDbCache, BaseCache

from .exceptions import BGGValueError


class CacheBackend(object):
    pass


class CacheBackendNone(CacheBackend):
    def __init__(self):
        self.cache = requests.Session()


class CacheBackendMemory(CacheBackend):
    """ Cache HTTP requests in memory """
    def __init__(self, ttl):
        try:
            int(ttl)
        except ValueError:
            raise BGGValueError
        backend = BaseCache()
        self.cache = requests_cache.CachedSession(backend=backend, expire_after=ttl, allowable_codes=(200,))


class CacheBackendSqlite(CacheBackend):
    def __init__(self, path, ttl, fast_save=True):
        try:
            int(ttl)
        except ValueError:
            raise BGGValueError

        self.cache = requests_cache.CachedSession(backend='sqlite', fast_save=fast_save, cache_name=path, expire_after=ttl, allowable_codes=(200,))


class CacheBackendDynamoDb(CacheBackend):
    def __init__(self, ttl, **kwargs):
        try:
            int(ttl)
        except ValueError:
            raise BGGValueError

        self.cache = requests_cache.CachedSession(backend='dynamodb', expire_after=ttl, allowable_codes=(200,), **kwargs)
