import json
from typing import Any, Optional

from redis.client import Redis

from .clients import current_redis_client
from .utils import temporary_key
from .adapters import BaseAdapter

__all__ = ["RedisDataMixin"]


class RedisDataMixin:
    __class__: type = None

    def __init__(self, key: str = None, *, init: Any = None, schema: Any = None):
        self.key: str = key or temporary_key()
        self.init = init
        self.schema = schema
        self.adapted_schema: Optional[BaseAdapter] = None if schema else json

        self.redis: Redis = current_redis_client()
        self.init and self._init(self.init)

    def _init(self, init: Any) -> None:
        pass

    def __del__(self):
        self.redis.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.redis
        except AttributeError:
            pass
        else:
            exc_type is not None and self.init and self.redis.delete(self.key)
            del self

    def loads(self, data: bytes) -> Any:
        if self.adapted_schema is not None:
            return self.adapted_schema.loads(data)

        for adapter in BaseAdapter.__subclasses__():
            target = adapter(self.schema)
            try:
                _data = target.loads(data)
            except Exception:  # noqa
                continue
            else:
                break
        else:
            target = json
            _data = target.loads(data)

        self.adapted_schema = target
        return _data

    def dumps(self, data: Any) -> str:
        if self.adapted_schema is not None:
            return self.adapted_schema.dumps(data)

        for adapter in BaseAdapter.__subclasses__():
            target = adapter(self.schema)
            try:
                _data = target.dumps(data)
            except Exception:  # noqa
                continue
            else:
                break
        else:
            target = json
            _data = target.dumps(data)

        self.adapted_schema = target
        return _data

    def bulk_dumps(self, *data: Any):
        for i in data:
            yield self.dumps(i)

    def bulk_loads(self, *data: bytes):
        for i in data:
            yield self.loads(i)

    def rename(self, new) -> None:
        assert self.redis.renamenx(self.key, new), f"duplicate key name {new}"
        self.key = new
