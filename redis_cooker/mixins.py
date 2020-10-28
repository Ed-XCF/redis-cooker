from typing import Optional, Any

from redis.client import Redis
from pydantic import Json
from pydantic.dataclasses import dataclass

from .clients import current_redis_client
from .utils import temporary_key

__all__ = ["RedisDataMixin"]


@dataclass
class _JsonLoader:
    obj: Json


class RedisDataMixin:
    __class__: type = None

    def __init__(self, key: Optional[str] = None, *, init: Optional[Any] = None):
        self.init: Any = init
        self.key: str = key or temporary_key()
        self.redis: Redis = current_redis_client()
        self.init and self._init(self.__class__(self.init))  # noqa

    def _init(self, init: __class__) -> None:
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

    @staticmethod
    def loads(data: bytes) -> Dict:
        return _JsonLoader(obj=data.decode("utf-8")).obj  # noqa

    def dumps(self, data: Dict) -> str:
        if self.model is None:
            return str(data)

        return self.model(**data).json()
