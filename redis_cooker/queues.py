from queue import Queue, LifoQueue

from .collections import RedisDeque, RedisList


class RedisQueue(Queue):
    def _init(self, maxsize: int) -> None:
        self.queue = RedisDeque()


class RedisLifoQueue(LifoQueue):
    def _init(self, maxsize: int) -> None:
        self.queue = RedisList()
