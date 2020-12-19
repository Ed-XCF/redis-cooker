import random
from typing import List

from attr import dataclass
from redis.exceptions import WatchError

from .clients import current_redis_client


@dataclass(frozen=True)
class Choice:
    name: str
    value: int


class ABNTest:
    key_delimiter = ":"

    def __init__(self, topic: str, choices: List[Choice]):
        assert all(i.value > 0 for i in choices), "Choice.value must > 0"
        prefix_key = self.key_delimiter.join(["RedisCooker", type(self).__name__, topic])
        self.keys = {self.key_delimiter.join([prefix_key, i.name]): i.value for i in choices}
        self.redis = current_redis_client()
        self._register_all_keys()

    def fetch(self) -> str:
        with self.redis.pipeline() as pipeline:
            while True:
                try:
                    keys = self.keys.keys()
                    pipeline.watch(*keys)

                    values = pipeline.mget(keys)
                    choices = [k for k, v in zip(keys, values) if int(v) > 0]

                    pipeline.multi()
                    if not choices:
                        pipeline.mset(self.keys)
                        pipeline.execute()
                        continue

                    choice: str = random.choice(choices)
                    pipeline.decr(choice)
                    pipeline.execute()
                    return choice.split(self.key_delimiter)[-1]
                except WatchError:
                    continue

    def _register_all_keys(self) -> None:
        """msetnx can not handle register new key into redis"""
        with self.redis.pipeline() as pipeline:
            for k, v in self.keys.items():
                pipeline.setnx(k, v)
            pipeline.execute()
