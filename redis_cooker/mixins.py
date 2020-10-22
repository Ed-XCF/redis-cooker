import uuid
from typing import Optional, Any

from redis.client import Redis

from .clients import current_redis_client

__all__ = ["RedisDataMixin"]


class RedisDataMixin:
    __class__: type = None

    def __init__(self, init=None, *, key: Optional[str] = None):
        self.init: Any = init
        self.key: str = key or str(uuid.uuid4())
        self.redis: Redis = current_redis_client()
        self.init and self._init(self.__class__(self.init))  # noqa

    def _init(self, init: __class__) -> None:
        pass

    @staticmethod
    def _decode(element: bytes) -> str:
        return element.decode("utf-8")

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
