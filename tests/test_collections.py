from copy import copy
from collections import deque, defaultdict

import pytest

from redis_cooker.collections import *
from redis_cooker.clients import *

set_connection_url('redis://:@127.0.0.1:6379/15')
client = current_redis_client()


class TestRedisMutableSet:
    key = "Testing:MutableSet"
    original = {"0", "1", "2"}

    def test_with(self):
        client.delete(self.key)
        with RedisMutableSet(self.key, init=self.original) as s:
            s.add(self.key)
        original = copy(self.original)
        original.add(self.key)
        assert RedisMutableSet(key=self.key) == original

        client.delete(self.key)
        with pytest.raises(AssertionError):
            with RedisMutableSet(self.key, init=self.original) as s:
                s.add(self.key)
                raise AssertionError
        assert RedisMutableSet(key=self.key) == set()

    def test__init(self):
        client.delete(self.key)
        s = RedisMutableSet(self.key, init=self.original)
        assert self.original == s

    def test___len__(self):
        client.delete(self.key)
        s = RedisMutableSet(self.key, init=self.original)
        assert len(self.original) == len(s)

    def test___iter__(self):
        client.delete(self.key)
        for i in RedisMutableSet(self.key, init=self.original):
            assert i in self.original

    def test___contains__(self):
        client.delete(self.key)
        s = RedisMutableSet(self.key, init=self.original)
        for i in self.original:
            assert i in s

    def test_add(self):
        client.delete(self.key)
        element = "3"
        s = RedisMutableSet(self.key, init=self.original)
        original = copy(self.original)

        s.add(element)
        original.add(element)
        assert s == original

    def test_discard(self):
        client.delete(self.key)
        element = "2"
        s = RedisMutableSet(self.key, init=self.original)
        original = copy(self.original)

        s.discard(element)
        original.discard(element)
        assert s == original

    def test_clear(self):
        client.delete(self.key)
        s = RedisMutableSet(self.key, init=self.original)
        original = copy(self.original)

        s.clear()
        original.clear()
        assert s == original

    def test_bulk_discard(self):
        client.delete(self.key)
        elements = {"0", "2"}
        s = RedisMutableSet(self.key, init=self.original)
        original = copy(self.original)

        assert s.bulk_discard(*elements) == len(elements)
        for i in elements:
            original.remove(i)
        assert s == original

    def test_update(self):
        client.delete(self.key)
        elements = {"0", "2"}
        s = RedisMutableSet(self.key, init=self.original)
        original = copy(self.original)

        s.update(*elements)
        original.update(*elements)
        assert s == original

    def test___isub__(self):
        key_a = self.key + "a"
        key_b = self.key + "b"
        client.delete(key_a)
        client.delete(key_b)
        a = RedisMutableSet(key_a, init=self.original)
        b = RedisMutableSet(key_b, init=self.original)
        original = copy(self.original)

        a -= b
        assert len(a) == 0
        b -= original
        assert len(b) == 0

    def test___ior__(self):
        key_a = self.key + "a"
        key_b = self.key + "b"
        client.delete(key_a)
        client.delete(key_b)
        a = RedisMutableSet(key_a, init={*self.original, "a"})
        b = RedisMutableSet(key_b, init={*self.original, "b"})
        original = copy(self.original)
        original.add("a")
        original.add("b")

        a |= b
        assert a == original
        b |= {*self.original, "a"}
        assert b == original

    def test___ixor__(self):
        key_a = self.key + "a"
        key_b = self.key + "b"
        client.delete(key_a)
        client.delete(key_b)
        a = RedisMutableSet(key_a, init={*self.original, "a"})
        b = RedisMutableSet(key_b, init={*self.original, "b"})
        a ^= b
        assert a == {"a", "b"}
        b ^= {*self.original, "a"}
        assert b == {"a", "b"}

    def test___iand__(self):
        key_a = self.key + "a"
        key_b = self.key + "b"
        client.delete(key_a)
        client.delete(key_b)
        a = RedisMutableSet(key_a, init={*self.original, "a"})
        b = RedisMutableSet(key_b, init={*self.original, "b"})
        a &= b
        assert a == self.original
        b &= {*self.original, "a"}
        assert b == self.original

    def test___str__(self):
        client.delete(self.key)
        s = RedisMutableSet(self.key, init=self.original)
        str(s)

    def test___repr__(self):
        client.delete(self.key)
        s = RedisMutableSet(self.key, init=self.original)
        repr(s)


class TestRedisString:
    key = "Testing:RedisString"
    original = "HelloWorld"

    def test__init(self):
        client.delete(self.key)
        s = RedisString(self.key, init=self.original)
        assert self.original == s

    def test___iter__(self):
        client.delete(self.key)
        count = 0
        for i in RedisString(self.key, init=self.original):
            assert i == self.original[count]
            count += 1

    def test___len__(self):
        client.delete(self.key)
        s = RedisString(self.key, init=self.original)
        assert len(self.original) == len(s)

    def test___reversed__(self):
        client.delete(self.key)
        s = RedisString(self.key, init=self.original)
        assert list(reversed(s)) == list(reversed(self.original))

    def test___getitem__(self):
        client.delete(self.key)
        s = RedisString(self.key, init=self.original)
        for index, value in enumerate(self.original):
            assert s[index] == value
        assert s[:] == self.original[:]
        assert s[1:5] == self.original[1:5]
        assert s[2:-1] == self.original[2:-1]
        assert s[-1:-5] == self.original[-1:-5]
        assert s[-5:-1] == self.original[-5:-1]
        assert s[3:100] == self.original[3:100]
        assert s[-3:-100] == self.original[-3:-100]

    def test_data(self):
        client.delete(self.key)
        s = RedisString(self.key)
        assert s == ""

        client.delete(self.key)
        for index, value in enumerate(RedisString(self.key, init=self.original)):
            assert value == self.original[index]


class TestRedisList:
    key = "Testing:RedisList"
    original = ['H', 'e', 'l', 'l', 'o', 'W', 'o', 'r', 'l', 'd']

    def test__init(self):
        client.delete(self.key)
        l = RedisList(self.key, init=self.original)
        assert self.original == l

    def test___iter__(self):
        client.delete(self.key)
        count = 0
        for i in RedisList(self.key, init=self.original):
            assert i == self.original[count]
            count += 1

    def test___len__(self):
        client.delete(self.key)
        l = RedisList(self.key, init=self.original)
        assert len(self.original) == len(l)

    def test_extend_and_pop(self):
        client.delete(self.key)
        other = "Z"
        l = RedisList(self.key, init=self.original)
        original = copy(self.original)

        l.extend([other])
        original.extend([other])
        assert l == original

    def test___iadd__(self):
        client.delete(self.key)
        other = "Z"
        l = RedisList(self.key, init=self.original)
        original = copy(self.original)

        l += [other]
        original += [other]
        assert l == original

    def test___imul__(self):
        client.delete(self.key)
        n = 2
        l = RedisList(self.key, init=self.original)
        original = copy(self.original)

        l *= n
        original *= n
        assert l == original

    def test_append(self):
        client.delete(self.key)
        other = "Z"
        l = RedisList(self.key, init=self.original)
        original = copy(self.original)

        l.append(other)
        original.append(other)
        assert l == original

    def test_insert(self):
        item = "item"
        for index in [-2, -1, 0, 1]:
            client.delete(self.key)
            l = RedisList(self.key, init=self.original)
            original = copy(self.original)
            l.insert(index, item)
            original.insert(index, item)
            assert l == original

    def test_pop(self):
        for index in [-2, -1, 0, 1]:
            client.delete(self.key)
            l = RedisList(self.key, init=self.original)
            original = copy(self.original)
            assert l.pop(index) == original.pop(index)
            assert l == original

    def test_remove(self):
        client.delete(self.key)
        item = "l"
        l = RedisList(self.key, init=self.original)
        original = copy(self.original)
        l.remove(item)
        original.remove(item)
        assert l == original

    def test_clear(self):
        client.delete(self.key)
        l = RedisList(self.key, init=self.original)
        original = copy(self.original)

        l.clear()
        original.clear()
        assert l == original

    def test_reverse(self):
        client.delete(self.key)
        l = RedisList(self.key, init=self.original)
        original = copy(self.original)

        l.reverse()
        original.reverse()
        assert l == original

    def test_sort(self):
        client.delete(self.key)
        l = RedisList(self.key, init=self.original)
        original = copy(self.original)
        l.sort()
        original.sort()
        assert l == original
        l.sort(reverse=True)
        original.sort(reverse=True)
        assert l == original

    def test___setitem__(self):
        item = "Z"
        for index in [-2, -1, 0, 1]:
            client.delete(self.key)
            l = RedisList(self.key, init=self.original)
            original = copy(self.original)
            l[index] = item
            original[index] = item
            assert l == original

        client.delete(self.key)
        l = RedisList(self.key)
        with pytest.raises(IndexError):
            l[0] = "H"
        l.append("oops")
        with pytest.raises(IndexError):
            l[10] = "H"

        client.delete(self.key)
        l = RedisList(self.key, init=self.original)
        with pytest.raises(TypeError):
            l[1:3] = 2

        client.delete(self.key)
        l = RedisList(self.key, init=self.original)
        with pytest.raises(ValueError):
            l[1:-1:2] = [1] * 1000

        client.delete(self.key)
        l = RedisList(self.key, init=self.original)
        original = copy(self.original)
        l[1:100] = [2,3,4]
        original[1:100] = [2,3,4]
        assert l == original

        client.delete(self.key)
        l = RedisList(self.key, init=self.original)
        original = copy(self.original)
        l[0:4] = ["a", "b", "c", "d", "e", "f", "g"]
        original[0:4] = ["a", "b", "c", "d", "e", "f", "g"]
        assert l == original

    def test___delitem__(self):
        for index in [-2, -1, 0, 1]:
            client.delete(self.key)
            l = RedisList(self.key, init=self.original)
            original = copy(self.original)
            del l[index]
            del original[index]
            assert l == original

        client.delete(self.key)
        l = RedisList(self.key)
        with pytest.raises(IndexError):
            del l[0]
        l.append("oops")
        with pytest.raises(IndexError):
            del l[10]

        client.delete(self.key)
        l = RedisList(self.key, init=self.original)
        del l[0:100]

        client.delete(self.key)
        l = RedisList(self.key, init=self.original)
        del l[0:5]

        client.delete(self.key)
        l = RedisList(self.key, init=self.original)
        del l[0:]

    def test___reversed__(self):
        client.delete(self.key)
        l = RedisList(self.key, init=self.original)
        assert list(reversed(l)) == list(reversed(self.original))

    def test___getitem__(self):
        for index in [-2, -1, 0, 1]:
            client.delete(self.key)
            l = RedisList(self.key, init=self.original)
            original = copy(self.original)
            assert l[index] == original[index]

        client.delete(self.key)
        l = RedisList(self.key, init=self.original)
        original = copy(self.original)
        assert l[:] == original[:]
        assert l[1:5] == original[1:5]
        assert l[2:-1] == original[2:-1]
        assert l[-1:-5] == original[-1:-5]
        assert l[-5:-1] == original[-5:-1]
        assert l[3:100] == original[3:100]
        assert l[-3:-100] == original[-3:-100]

        client.delete(self.key)
        l = RedisList(self.key)
        assert l[:] == []
        assert l[1:5] == []
        with pytest.raises(IndexError):
            _ = l[0]

    def test_data(self):
        client.delete(self.key)
        l = RedisList(self.key)
        assert l == []


class TestRedisDict:
    key = "Testing:RedisDict"
    original = {"Hello": "World"}

    def test__init(self):
        client.delete(self.key)
        d = RedisDict(self.key, init=self.original)
        assert self.original == d

    def test___len__(self):
        client.delete(self.key)
        d = RedisDict(self.key, init=self.original)
        assert len(self.original) == len(d)

    def test___contains__(self):
        client.delete(self.key)
        d = RedisDict(self.key, init=self.original)
        for k in self.original.keys():
            assert k in d

    def test_items(self):
        client.delete(self.key)
        for k, v in RedisDict(self.key, init=self.original).items():
            assert k in self.original
            assert v == self.original[k]

    def test___iter__(self):
        client.delete(self.key)
        for i in RedisDict(self.key, init=self.original):
            assert i in self.original

    def test_values(self):
        client.delete(self.key)
        for i in RedisDict(self.key, init=self.original).values():
            pass

    def test___getitem__(self):
        client.delete(self.key)
        d = RedisDict(self.key, init=self.original)
        for k, v in self.original.items():
            assert d[k] == v

        with pytest.raises(KeyError):
            _ = d["oops"]

    def test___eq__(self):
        client.delete(self.key)
        d1 = RedisDict(self.key, init=self.original)
        d2 = RedisDict(self.key, init=self.original)
        assert d1 == self.original
        assert d1 == d2
        assert not (d1 == 3)

    def test___setitem__(self):
        client.delete(self.key)
        d = RedisDict(self.key, init={})
        for k, v in self.original.items():
            d[k] = v
        assert d == self.original

    def test___delitem__(self):
        client.delete(self.key)
        d = RedisDict(self.key, init=self.original)
        original = copy(self.original)
        for i in self.original.keys():
            del d[i]
            del original[i]
        assert d == original

        with pytest.raises(KeyError):
            del d["oops"]

    def test_clear(self):
        client.delete(self.key)
        d = RedisDict(self.key, init=self.original)
        original = copy(self.original)
        d.clear()
        original.clear()
        assert d == original

    def test_data(self):
        client.delete(self.key)
        d = RedisDict(self.key, init=self.original)
        original = copy(self.original)
        assert d.data == original

    def test_update(self):
        client.delete(self.key)
        d = RedisDict(self.key, init=self.original)
        original = copy(self.original)
        d.update(x="x")
        original.update(x="x")
        assert d == original

        client.delete(self.key)
        d = RedisDict(self.key, init=self.original)
        original = copy(self.original)
        d.update({"y": "y"})
        original.update({"y": "y"})
        assert d == original

        client.delete(self.key)
        d = RedisDict(self.key, init=self.original)
        original = copy(self.original)
        d.update({"y": "y"}, x="x")
        original.update({"y": "y"}, x="x")
        assert d == original

        client.delete(self.key)
        d = RedisDict(self.key, init=self.original)
        with pytest.raises(TypeError):
            d.update()
            d.update(1, 2)

    def test_fromkeys(self):
        keys = ["a", "b", "c"]
        value = "abc"
        d = RedisDict.fromkeys(keys, value)
        original = dict.fromkeys(keys, value)
        assert d == original

        _ = RedisDict.fromkeys(keys)

    def test___str__(self):
        client.delete(self.key)
        d = RedisDict(self.key, init=self.original)
        original = copy(self.original)
        assert str(d) == str(original)

    def test___repr__(self):
        client.delete(self.key)
        d = RedisDict(self.key, init=self.original)
        original = copy(self.original)
        assert repr(d) == repr(original)


class TestRedisDeque:
    key = "Testing:RedisDeque"
    original = ['H', 'e', 'l', 'l', 'o', 'W', 'o', 'r', 'l', 'd']

    def test_appendleft(self):
        client.delete(self.key)
        l = RedisDeque(self.key, init=self.original)
        l.appendleft('Z')
        d = deque(self.original)
        d.appendleft('Z')
        assert l == d

    def test_extendleft(self):
        client.delete(self.key)
        elements = ["X", "Y", "Z"]
        l = RedisDeque(self.key, init=self.original)
        l.extendleft(elements)
        d = deque(self.original)
        d.extendleft(elements)
        assert l == d

    def test_popleft(self):
        client.delete(self.key)
        l = RedisDeque(self.key, init=self.original)
        d = deque(self.original)
        d.popleft() == l.popleft()
        assert l == d

        client.delete(self.key)
        with pytest.raises(IndexError):
            l = RedisDeque(self.key)
            l.popleft()

    def test_rotate(self):
        for i in [-20, -5, 0, 5, 20]:
            print(i)
            client.delete(self.key)
            l = RedisDeque(self.key, init=self.original)
            d = deque(self.original)
            l.rotate(i)
            d.rotate(i)
            assert l == d

    def test_sort(self):
        client.delete(self.key)
        l = RedisDeque(self.key, init=self.original)
        with pytest.raises(AttributeError):
            l.sort()

    def test___getitem__(self):
        client.delete(self.key)
        l = RedisDeque(self.key, init=self.original)
        with pytest.raises(TypeError):
            _ = l[1:2]
        assert l[0] == self.original[0]

    def test___setitem__(self):
        client.delete(self.key)
        l = RedisDeque(self.key, init=self.original)
        with pytest.raises(TypeError):
            l[1:2] = 6
        l[0] = 7
        assert l == deque([7, *self.original[1:]])

    def test___delitem__(self):
        client.delete(self.key)
        l = RedisDeque(self.key, init=self.original)
        with pytest.raises(TypeError):
            del l[1:2]
        del l[0]
        assert l == deque(self.original[1:])


class TestRedisDefaultDict:
    key = "Testing:RedisDict"
    original = {"Hello": "World"}

    def test___missing__(self):
        client.delete(self.key)

        def default_factory():
            return "oops"

        r = RedisDefaultDict(self.key, default_factory=default_factory, init=self.original)
        d = defaultdict(default_factory, self.original)
        assert r["Hello"] == d["Hello"]
        assert r["WOW"] == default_factory()
        assert ("WOW" in r) != ("WOW" in d)
        _ = d["WOW"]
        assert ("WOW" in r) == ("WOW" in d)
