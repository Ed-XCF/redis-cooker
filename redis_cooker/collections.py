import uuid
import itertools
from collections import abc, UserString, UserList, UserDict

from .atomic import run_as_lua
from .mixins import RedisDataMixin

__all__ = ["RedisMutableSet", "RedisString", "RedisList", "RedisDict"]


class RedisMutableSet(RedisDataMixin, abc.MutableSet):
    __class__ = set

    @run_as_lua(list)
    def _init(self, init: __class__) -> None:
        """
        redis.call("DEL", KEYS[1])
        redis.call("SADD", KEYS[1], unpack(ARGV))
        """
        pass

    def __len__(self):
        return self.redis.scard(self.key)

    def __iter__(self):
        for i in self.redis.sscan_iter(self.key):
            yield self._decode(i)

    def __contains__(self, item):
        return self.redis.sismember(self.key, item)

    def add(self, element) -> int:
        return self.redis.sadd(self.key, element)

    def discard(self, element) -> int:
        return self.redis.srem(self.key, element)

    def clear(self) -> None:
        self.redis.delete(self.key)

    def bulk_discard(self, *element) -> int:
        return self.redis.srem(self.key, *element)

    def update(self, *element) -> None:
        self.redis.sadd(self.key, *element)

    def __str__(self):
        return str(self.__class__(self))

    def __repr__(self):
        return repr(self.__class__(self))

    @classmethod
    def _from_iterable(cls, it):
        return cls.__class__(it)

    def __isub__(self, other):
        if isinstance(other, type(self)):
            self.redis.sdiffstore(self.key, [self.key, other.key])
        else:
            self.bulk_discard(*other)
        return self

    def __ior__(self, other):
        if isinstance(other, type(self)):
            self.redis.sunionstore(self.key, [self.key, other.key])
        else:
            self.update(*other)
        return self

    def __ixor__(self, other):
        if isinstance(other, type(self)):
            temp_key1, temp_key2 = str(uuid.uuid4()), str(uuid.uuid4())
            with self.redis.pipeline() as pipe:
                pipe.sdiffstore(temp_key1, [self.key, other.key])
                pipe.sdiffstore(temp_key2, [other.key, self.key])
                pipe.sunionstore(self.key, [temp_key1, temp_key2])
                pipe.delete(temp_key1)
                pipe.delete(temp_key2)
                pipe.execute()
        else:
            temp_key1, temp_key2, temp_key3 = str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())
            with self.redis.pipeline() as pipe:
                pipe.sadd(temp_key1, *other)
                pipe.sdiffstore(temp_key2, [self.key, temp_key1])
                pipe.sdiffstore(temp_key3, [temp_key1, self.key])
                pipe.sunionstore(self.key, [temp_key2, temp_key3])
                pipe.delete(temp_key1)
                pipe.delete(temp_key2)
                pipe.delete(temp_key3)
                pipe.execute()
        return self

    def __iand__(self, other):
        if isinstance(other, type(self)):
            self.redis.sinterstore(self.key, [self.key, other.key])
        else:
            temp_key = str(uuid.uuid4())
            with self.redis.pipeline() as pipe:
                pipe.sadd(temp_key, *other)
                pipe.sinterstore(self.key, [self.key, temp_key])
                pipe.delete(temp_key)
                pipe.execute()
        return self


class RedisString(RedisDataMixin, UserString):
    __class__ = str

    def _init(self, init: __class__) -> None:
        self.redis.set(self.key, init)

    @property
    def data(self) -> __class__:
        return self._decode(self.redis.get(self.key))

    def __iter__(self):
        for i in self.data:
            yield i

    def __len__(self):
        return self.redis.strlen(self.key)

    def __reversed__(self):
        return reversed(self.data)

    def __getitem__(self, index):
        return self._decode(self.redis.getrange(self.key, index, index))


class RedisList(RedisDataMixin, UserList):
    __class__ = list

    @run_as_lua(lambda init: init)
    def _init(self, init: __class__) -> None:
        """
        redis.call("DEL", KEYS[1])
        redis.call("RPUSH", KEYS[1], unpack(ARGV))
        """
        pass

    def __iter__(self):
        for i in self.redis.lrange(self.key, 0, -1):
            yield self._decode(i)

    @property
    def data(self) -> __class__:
        return self.__class__(self)

    def extend(self, other) -> None:
        self.redis.rpush(self.key, *other)

    def __iadd__(self, other):
        self.extend(other)
        return self

    def __imul__(self, n):
        self.extend(self.data * (n - 1))
        return self

    def append(self, item) -> None:
        self.extend([item])

    @run_as_lua(lambda index, item: [index if index >= 0 else index - 1, item])
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
            self.redis.lpush(self.key, item)
        else:
            self._redis_insert(index, item)

    @run_as_lua(lambda index: [index])
    def _redis_pop(self, index: int) -> str:
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

    def pop(self, index: int = -1) -> str:
        if index == -1:
            element = self.redis.rpop(self.key)
        elif index == 0:
            element = self.redis.lpop(self.key)
        else:
            element = self._redis_pop(index)

        return self._decode(element)

    def remove(self, item) -> None:
        self.redis.lrem(self.key, 1, item)

    def clear(self) -> None:
        self.redis.delete(self.key)

    @run_as_lua(list)
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

    def __setitem__(self, index, value):
        self.redis.lset(self.key, index, value)

    def __delitem__(self, index):
        self.pop(index)

    def __reversed__(self):
        return reversed(self.data)

    def __len__(self):
        return self.redis.llen(self.key)

    def __getitem__(self, index):
        if not isinstance(index, slice):
            return self._decode(self.redis.lrange(self.key, index, index)[0])

        if index.start is None and index.stop is None:
            return self.data

        start = index.start or 0
        stop = index.stop or 0

        return [
            self._decode(i)
            for i in self.redis.lrange(
                self.key,
                start,
                stop - 1,
            )
        ]


class RedisDict(RedisDataMixin, UserDict):
    __class__ = dict

    @run_as_lua(lambda init: list(itertools.chain.from_iterable(init.items())))
    def _init(self, init: __class__) -> None:
        """
        redis.call("DEL", KEYS[1])
        redis.call("HMSET", KEYS[1], unpack(ARGV))
        """
        pass

    def __len__(self):
        return self.redis.hlen(self.key)

    def __contains__(self, item):
        return self.redis.hexists(self.key, item)

    def items(self):
        for k, v in self.redis.hscan_iter(self.key):
            yield self._decode(k), self._decode(v)

    def __iter__(self):
        for k, _ in self.items():
            yield k

    def values(self):
        for _, v in self.items():
            yield v

    def __getitem__(self, item):
        try:
            return self._decode(self.redis.hget(self.key, item))
        except AttributeError:
            raise KeyError(item)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.key == other.key
        elif isinstance(other, abc.Mapping):
            return super().__eq__(other)
        else:
            return False

    def __setitem__(self, key, value):
        self.redis.hset(self.key, key, value)

    def __delitem__(self, key):
        self.redis.hdel(self.key, key)

    def clear(self) -> None:
        self.redis.delete(self.key)

    @property
    def data(self) -> __class__:
        return self.__class__(self.items())

    def update(*args, **kwds):
        if not args:
            raise TypeError("descriptor 'update' of 'MutableMapping' object needs an argument")
        self, *args = args
        if len(args) > 1:
            raise TypeError(f"update expected at most 1 arguments, got {len(args)}")

        args and kwds.update(args[0])
        kwds and self.redis.hmset(self.key, kwds)

    @classmethod
    def fromkeys(cls, iterable, value = None):
        if value is None:
            return cls()
        else:
            return cls(dict.fromkeys(iterable, value))

    def __str__(self):
        return str(self.__class__(self.items()))

    def __repr__(self):
        return repr(self.__class__(self.items()))
