from queue import Queue, LifoQueue

from .collections import RedisDeque, RedisList

__all__ = ["RedisQueue", "RedisLifoQueue"]


class RedisQueue(Queue):
    def _init(self, maxsize: int) -> None:
        self.queue = RedisDeque()


class RedisLifoQueue(LifoQueue):
    def _init(self, maxsize: int) -> None:
        self.queue = RedisList()
