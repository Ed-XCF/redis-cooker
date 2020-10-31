import json
from typing import Any, Type

from redis.client import Redis
from pydantic import BaseModel

from .clients import current_redis_client
from .utils import temporary_key

__all__ = ["RedisDataMixin"]


class RedisDataMixin:
    __class__: type = None

    def __init__(self, key: str = None, *, init: Any = None, model: Type[BaseModel] = None):
        self.key: str = key or temporary_key()
        self.init = init
        self.model = model

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
            exc_type is not None and self.init is not None and self.redis.delete(self.key)
            del self

    def loads(self, data: bytes) -> Any:
        if self.model is None:
            return json.loads(data)

        return self.model.parse_raw(data).dict()

    def dumps(self, data: Any) -> str:
        if self.model is not None:
            data = self.model(**data).dict()

        return json.dumps(data)

    def bulk_dumps(self, *data: Any):
        for i in data:
            yield self.dumps(i)

    def bulk_loads(self, *data: bytes):
        for i in data:
            yield self.loads(i)

    def rename(self, new):
        assert self.redis.renamenx(self.key, new), f"duplicate key name {new}"
        self.key = new
