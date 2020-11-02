import itertools
from collections import abc, UserString, UserList, UserDict
from typing import List, Dict, Set, Any

from redis.exceptions import ResponseError

from .atomic import run_as_lua
from .mixins import RedisDataMixin
from .utils import temporary_key

__all__ = ["RedisMutableSet", "RedisString", "RedisList", "RedisDict"]


class RedisMutableSet(RedisDataMixin, abc.MutableSet):
    @run_as_lua(lambda self, init: list(self.bulk_dumps(*init)))
    def _init(self, init: Set) -> None:
        """
        if redis.call("SETNX", KEYS[1], "__PLACEHOLDER__") == 1
        then
            redis.call("DEL", KEYS[1])
            redis.call("SADD", KEYS[1], unpack(ARGV))
        end
        """
        pass

    def __len__(self) -> int:
        return self.redis.scard(self.key)

    def __iter__(self):
        for i in self.redis.sscan_iter(self.key):
            yield self.loads(i)

    def __contains__(self, item) -> bool:
        return self.redis.sismember(self.key, self.dumps(item))

    def add(self, element) -> None:
        self.redis.sadd(self.key, self.dumps(element))

    def discard(self, element) -> None:
        self.redis.srem(self.key, self.dumps(element))

    def clear(self) -> None:
        self.redis.delete(self.key)

    def bulk_discard(self, *element) -> int:
        return self.redis.srem(self.key, *self.bulk_dumps(*element))

    def update(self, *element) -> None:
        self.redis.sadd(self.key, *self.bulk_dumps(*element))

    def __str__(self) -> str:
        return "{" + ", ".join(str(i) for i in self) + "}"

    def __repr__(self) -> str:
        return str(self)

    @classmethod
    def _from_iterable(cls, it) -> Set:
        return set(it)

    def __isub__(self, other) -> "RedisMutableSet":
        if isinstance(other, type(self)):
            self.redis.sdiffstore(self.key, [self.key, other.key])
        else:
            self.bulk_discard(*other)
        return self

    def __ior__(self, other) -> "RedisMutableSet":
        if isinstance(other, type(self)):
            self.redis.sunionstore(self.key, [self.key, other.key])
        else:
            self.update(*other)
        return self

    def __ixor__(self, other) -> "RedisMutableSet":
        if isinstance(other, type(self)):
            temp_key1, temp_key2 = temporary_key(), temporary_key()
            with self.redis.pipeline() as pipe:
                pipe.sdiffstore(temp_key1, [self.key, other.key])
                pipe.sdiffstore(temp_key2, [other.key, self.key])
                pipe.sunionstore(self.key, [temp_key1, temp_key2])
                pipe.delete(temp_key1)
                pipe.delete(temp_key2)
                pipe.execute()
        else:
            temp_key1, temp_key2, temp_key3 = temporary_key(), temporary_key(), temporary_key()
            with self.redis.pipeline() as pipe:
                pipe.sadd(temp_key1, *self.bulk_dumps(*other))
                pipe.sdiffstore(temp_key2, [self.key, temp_key1])
                pipe.sdiffstore(temp_key3, [temp_key1, self.key])
                pipe.sunionstore(self.key, [temp_key2, temp_key3])
                pipe.delete(temp_key1)
                pipe.delete(temp_key2)
                pipe.delete(temp_key3)
                pipe.execute()
        return self

    def __iand__(self, other) -> "RedisMutableSet":
        if isinstance(other, type(self)):
            self.redis.sinterstore(self.key, [self.key, other.key])
        else:
            temp_key = temporary_key()
            with self.redis.pipeline() as pipe:
                pipe.sadd(temp_key, *self.bulk_dumps(*other))
                pipe.sinterstore(self.key, [self.key, temp_key])
                pipe.delete(temp_key)
                pipe.execute()
        return self


class RedisString(RedisDataMixin, UserString):
    __class__ = str

    def _init(self, init: str) -> None:
        self.redis.setnx(self.key, init)

    @property
    def data(self) -> str:
        return (self.redis.get(self.key) or b"").decode("utf-8")


class RedisList(RedisDataMixin, UserList):
    __class__ = list

    @run_as_lua(lambda self, init: list(self.bulk_dumps(*init)))
    def _init(self, init: List) -> None:
        """
        if redis.call("SETNX", KEYS[1], "__PLACEHOLDER__") == 1
        then
            redis.call("DEL", KEYS[1])
            redis.call("RPUSH", KEYS[1], unpack(ARGV))
        end
        """
        pass

    def __iter__(self):
        for i in self.redis.lrange(self.key, 0, -1):
            yield self.loads(i)

    @property
    def data(self) -> List:
        return list(self)

    def extend(self, other) -> None:
        self.redis.rpush(self.key, *self.bulk_dumps(*other))

    def __iadd__(self, other) -> "RedisList":
        self.extend(other)
        return self

    def __imul__(self, n) -> "RedisList":
        self.extend(self.data * (n - 1))
        return self

    def append(self, item) -> None:
        self.extend([item])

    @run_as_lua(lambda self, index, item: [index if index >= 0 else index - 1, item])
    def _redis_insert(self, index: int, item: str) -> None:
        """
        local input_index = tonumber(ARGV[1])
        local new_index = nil
        local where = nil
        if input_index < 0
        then
            where = "AFTER"
            new_index = input_index - 1
        else
            where = "BEFORE"
            new_index = input_index + 1
        end
        local target = redis.call("LINDEX", KEYS[1], input_index)
        local replace_mark = "__REPLACE_MARK__"
        redis.call("LSET", KEYS[1], input_index, replace_mark)

        redis.call("LINSERT", KEYS[1], where, replace_mark, ARGV[2])
        redis.call("LSET", KEYS[1], new_index, target)
        """
        pass

    def insert(self, index: int, item: str) -> None:
        if index == 0:
            self.redis.lpush(self.key, self.dumps(item))
        else:
            self._redis_insert(index, self.dumps(item))

    @run_as_lua(lambda self, index: [index])
    def _redis_pop(self, index: int) -> bytes:
        """
        local index = ARGV[1]
        if index == "-1"
        then
            index = redis.call("LLEN", KEYS[1]) - 1
        end

        local temp = redis.call("LINDEX", KEYS[1], index)
        local deleted_mark = "_DELETED_MARK_"
        redis.call("LSET", KEYS[1], index, deleted_mark)
        redis.call("LREM", KEYS[1], 0, deleted_mark)
        return temp
        """
        pass

    def pop(self, index: int = -1) -> Any:
        if index == -1:
            element = self.redis.rpop(self.key)
        elif index == 0:
            element = self.redis.lpop(self.key)
        else:
            element = self._redis_pop(index)

        return self.loads(element)

    def remove(self, item) -> None:
        self.redis.lrem(self.key, 1, self.dumps(item))

    def clear(self) -> None:
        self.redis.delete(self.key)

    @run_as_lua(lambda self: [])
    def reverse(self) -> None:
        """
        local origin = redis.call("LRANGE", KEYS[1], 0, -1)
        local reversed = {}

        for i = 1, #origin do
            local key = #origin
            reversed[i] = table.remove(origin)
        end

        redis.call("DEL", KEYS[1])
        redis.call("RPUSH", KEYS[1], unpack(reversed))
        """
        pass

    def sort(self, reverse=False) -> None:
        self.redis.sort(self.key, desc=reverse, alpha=True, store=self.key)

    def __setitem__(self, index, value) -> None:
        try:
            self.redis.lset(self.key, index, self.dumps(value))
        except ResponseError as e:
            if str(e) in ("no such key", "index out of range"):
                _ = [][0]
            raise

    def __delitem__(self, index) -> None:
        try:
            self.pop(index)
        except TypeError as e:
            if str(e) == "the JSON object must be str, bytes or bytearray, not 'NoneType'":
                del [][index]
            raise
        except ResponseError as e:
            if str(e).endswith("ERR index out of range "):
                del [][index]
            raise

    def __len__(self) -> int:
        return self.redis.llen(self.key)

    def __getitem__(self, index) -> Any:
        if not isinstance(index, slice):
            return self.loads(self.redis.lrange(self.key, index, index)[0])

        if index.start is None and index.stop is None:
            return self.data

        start, stop = index.start or 0, (index.stop or 0) - 1
        return list(self.bulk_loads(*self.redis.lrange(self.key, start, stop)))


class RedisDict(RedisDataMixin, UserDict):
    __class__ = dict

    @run_as_lua(lambda self, init: list(itertools.chain.from_iterable((
        (k, self.dumps(v))
         for k, v in init.items()
    ))))
    def _init(self, init: Dict) -> None:
        """
        if redis.call("SETNX", KEYS[1], "__PLACEHOLDER__") == 1
        then
            redis.call("DEL", KEYS[1])
            redis.call("HMSET", KEYS[1], unpack(ARGV))
        end
        """
        pass

    def __len__(self) -> int:
        return self.redis.hlen(self.key)

    def __contains__(self, item) -> bool:
        return self.redis.hexists(self.key, item)

    def items(self):
        for k, v in self.redis.hscan_iter(self.key):
            yield k.decode("utf-8"), self.loads(v)

    def __iter__(self):
        for k, _ in self.items():
            yield k

    def values(self):
        for _, v in self.items():
            yield v

    def __getitem__(self, item) -> Any:
        value = self.redis.hget(self.key, item)
        if value is None:
            _ = {}[item]

        return self.loads(value)

    def __eq__(self, other) -> bool:
        if isinstance(other, type(self)):
            return self.key == other.key
        elif isinstance(other, abc.Mapping):
            return super().__eq__(other)
        else:
            return False

    def __setitem__(self, key, value) -> None:
        self.redis.hset(self.key, key, self.dumps(value))

    def __delitem__(self, key) -> None:
        if self.redis.hdel(self.key, key) == 0:
            del {}[key]

    def clear(self) -> None:
        self.redis.delete(self.key)

    @property
    def data(self) -> Dict:
        return dict(self.items())

    def update(self, *args, **kwds) -> None:
        if len(args) > 1:
            raise TypeError(f"update expected at most 1 arguments, got {len(args)}")

        args and kwds.update(args[0])
        kwds and self.redis.hmset(self.key, {k: self.dumps(v) for k, v in kwds.items()})

    @classmethod
    def fromkeys(cls, iterable, value = None) -> "RedisDict":
        if value is None:
            return cls()
        else:
            return cls(init=dict.fromkeys(iterable, value))

    def __str__(self) -> str:
        return str(dict(self.items()))

    def __repr__(self) -> str:
        return repr(dict(self.items()))
