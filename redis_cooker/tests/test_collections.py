from copy import copy

import pytest

from ..collections import *
from ..clients import set_connection_url

set_connection_url('redis://:@127.0.0.1:6379/15')


class TestRedisMutableSet:
    key = "Testing:MutableSet"
    original = {"0", "1", "2"}

    def test_with(self):
        with RedisMutableSet(self.original, key=self.key) as s:
            s.add(self.key)
        original = copy(self.original)
        original.add(self.key)
        assert RedisMutableSet(key=self.key) == original

        with pytest.raises(AssertionError):
            with RedisMutableSet(self.original, key=self.key) as s:
                s.add(self.key)
                raise AssertionError
        assert RedisMutableSet(key=self.key) == set()

    def test__init(self):
        s = RedisMutableSet(self.original, key=self.key)
        assert self.original == s

    def test___len__(self):
        s = RedisMutableSet(self.original, key=self.key)
        assert len(self.original) == len(s)

    def test___iter__(self):
        for i in RedisMutableSet(self.original, key=self.key):
            assert i in self.original

    def test___contains__(self):
        s = RedisMutableSet(self.original, key=self.key)
        for i in self.original:
            assert i in s

    def test_add(self):
        element = "3"
        s = RedisMutableSet(self.original, key=self.key)
        original = copy(self.original)

        assert s.add(element) == 1
        original.add(element)
        assert s == original

    def test_discard(self):
        element = "2"
        s = RedisMutableSet(self.original, key=self.key)
        original = copy(self.original)

        assert s.discard(element) == 1
        original.discard(element)
        assert s == original

    def test_clear(self):
        s = RedisMutableSet(self.original, key=self.key)
        original = copy(self.original)

        s.clear()
        original.clear()
        assert s == original

    def test_bulk_discard(self):
        elements = {"0", "2"}
        s = RedisMutableSet(self.original, key=self.key)
        original = copy(self.original)

        assert s.bulk_discard(*elements) == len(elements)
        for i in elements:
            original.remove(i)
        assert s == original

    def test_update(self):
        elements = {"0", "2"}
        s = RedisMutableSet(self.original, key=self.key)
        original = copy(self.original)

        s.update(*elements)
        original.update(*elements)
        assert s == original

    def test___isub__(self):
        a = RedisMutableSet(self.original, key=self.key + "a")
        b = RedisMutableSet(self.original, key=self.key + "b")
        original = copy(self.original)

        a -= b
        assert len(a) == 0
        b -= original
        assert len(b) == 0

    def test___ior__(self):
        a = RedisMutableSet({*self.original, "a"}, key=self.key + "a")
        b = RedisMutableSet({*self.original, "b"}, key=self.key + "b")
        original = copy(self.original)
        original.add("a")
        original.add("b")

        a |= b
        assert a == original
        b |= {*self.original, "a"}
        assert b == original

    def test___ixor__(self):
        a = RedisMutableSet({*self.original, "a"}, key=self.key + "a")
        b = RedisMutableSet({*self.original, "b"}, key=self.key + "b")
        a ^= b
        assert a == {"a", "b"}
        b ^= {*self.original, "a"}
        assert b == {"a", "b"}

    def test___iand__(self):
        a = RedisMutableSet({*self.original, "a"}, key=self.key + "a")
        b = RedisMutableSet({*self.original, "b"}, key=self.key + "b")
        a &= b
        assert a == self.original
        b &= {*self.original, "a"}
        assert b == self.original

    def test___str__(self):
        a = RedisMutableSet(self.original, key=self.key)
        original = copy(self.original)
        assert str(a) == str(original)

    def test___repr__(self):
        a = RedisMutableSet(self.original, key=self.key)
        original = copy(self.original)
        assert repr(a) == repr(original)


class TestRedisString:
    key = "Testing:RedisString"
    original = "HelloWorld"

    def test__init(self):
        s = RedisString(self.original, key=self.key)
        assert self.original == s

    def test___iter__(self):
        count = 0
        for i in RedisString(self.original, key=self.key):
            assert i == self.original[count]
            count += 1

    def test___len__(self):
        s = RedisString(self.original, key=self.key)
        assert len(self.original) == len(s)

    def test___reversed__(self):
        s = RedisString(self.original, key=self.key)
        assert list(reversed(s)) == list(reversed(self.original))

    def test___getitem__(self):
        s = RedisString(self.original, key=self.key)
        for index, value in enumerate(self.original):
            assert s[index] == value


class TestRedisList:
    key = "Testing:RedisList"
    original = ['H', 'e', 'l', 'l', 'o', 'W', 'o', 'r', 'l', 'd']

    def test__init(self):
        l = RedisList(self.original, key=self.key)
        assert self.original == l

    def test___iter__(self):
        count = 0
        for i in RedisList(self.original, key=self.key):
            assert i == self.original[count]
            count += 1

    def test___len__(self):
        l = RedisList(self.original, key=self.key)
        assert len(self.original) == len(l)

    def test_extend_and_pop(self):
        other = "Z"
        l = RedisList(self.original, key=self.key)
        original = copy(self.original)

        l.extend([other])
        original.extend([other])
        assert l == original

    def test___iadd__(self):
        other = "Z"
        l = RedisList(self.original, key=self.key)
        original = copy(self.original)

        l += [other]
        original += [other]
        assert l == original

    def test___imul__(self):
        n = 2
        l = RedisList(self.original, key=self.key)
        original = copy(self.original)

        l *= n
        original *= n
        assert l == original

    def test_append(self):
        other = "Z"
        l = RedisList(self.original, key=self.key)
        original = copy(self.original)

        l.append(other)
        original.append(other)
        assert l == original

    def test_insert(self):
        item = "item"
        for index in [-2, -1, 0, 1]:
            l = RedisList(self.original, key=self.key)
            original = copy(self.original)
            l.insert(index, item)
            original.insert(index, item)
            assert l == original

    def test_pop(self):
        for index in [-2, -1, 0, 1]:
            l = RedisList(self.original, key=self.key)
            original = copy(self.original)
            assert l.pop(index) == original.pop(index)
            assert l == original

    def test_remove(self):
        item = "l"
        l = RedisList(self.original, key=self.key)
        original = copy(self.original)
        l.remove(item)
        original.remove(item)
        assert l == original

    def test_clear(self):
        l = RedisList(self.original, key=self.key)
        original = copy(self.original)

        l.clear()
        original.clear()
        assert l == original

    def test_reverse(self):
        l = RedisList(self.original, key=self.key)
        original = copy(self.original)

        l.reverse()
        original.reverse()
        assert l == original

    def test_sort(self):
        l = RedisList(self.original, key=self.key)
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
            l = RedisList(self.original, key=self.key)
            original = copy(self.original)
            l[index] = item
            original[index] = item
            assert l == original

    def test___delitem__(self):
        for index in [-2, -1, 0, 1]:
            l = RedisList(self.original, key=self.key)
            original = copy(self.original)
            del l[index]
            del original[index]
            assert l == original

    def test___reversed__(self):
        l = RedisList(self.original, key=self.key)
        assert list(reversed(l)) == list(reversed(self.original))

    def test___getitem__(self):
        for index in [-2, -1, 0, 1]:
            l = RedisList(self.original, key=self.key)
            original = copy(self.original)
            assert l[index] == original[index]

        l = RedisList(self.original, key=self.key)
        original = copy(self.original)
        assert l[:] == original[:]
        assert l[1:5] == original[1:5]
        assert l[2:-1] == original[2:-1]
        assert l[-1:-5] == original[-1:-5]
        assert l[-5:-1] == original[-5:-1]
        assert l[3:100] == original[3:100]
        assert l[-3:-100] == original[-3:-100]


class TestRedisDict:
    key = "Testing:RedisDict"
    original = {"Hello": "World"}

    def test__init(self):
        d = RedisDict(self.original, key=self.key)
        assert self.original == d

    def test___len__(self):
        d = RedisDict(self.original, key=self.key)
        assert len(self.original) == len(d)

    def test___contains__(self):
        d = RedisDict(self.original, key=self.key)
        for k in self.original.keys():
            assert k in d

    def test_items(self):
        for k, v in RedisDict(self.original, key=self.key).items():
            assert k in self.original
            assert v == self.original[k]

    def test___iter__(self):
        for i in RedisDict(self.original, key=self.key):
            assert i in self.original

    def test_values(self):
        for i in RedisDict(self.original, key=self.key).values():
            pass

    def test___getitem__(self):
        d = RedisDict(self.original, key=self.key)
        for k, v in self.original.items():
            assert d[k] == v

        with pytest.raises(KeyError):
            _ = d["oops"]

    def test___eq__(self):
        d1 = RedisDict(self.original, key=self.key)
        d2 = RedisDict(self.original, key=self.key)
        assert d1 == self.original
        assert d1 == d2
        assert not (d1 == 3)

    def test___setitem__(self):
        d = RedisDict({}, key=self.key)
        for k, v in self.original.items():
            d[k] = v
        assert d == self.original

    def test___delitem__(self):
        d = RedisDict(self.original, key=self.key)
        original = copy(self.original)
        for i in self.original.keys():
            del d[i]
            del original[i]
        assert d == original

    def test_clear(self):
        d = RedisDict(self.original, key=self.key)
        original = copy(self.original)
        d.clear()
        original.clear()
        assert d == original

    def test_data(self):
        d = RedisDict(self.original, key=self.key)
        original = copy(self.original)
        assert d.data == original

    def test_update(self):
        d = RedisDict(self.original, key=self.key)
        original = copy(self.original)
        d.update(x="x")
        original.update(x="x")
        assert d == original

        d = RedisDict(self.original, key=self.key)
        original = copy(self.original)
        d.update({"y": "y"})
        original.update({"y": "y"})
        assert d == original

        d = RedisDict(self.original, key=self.key)
        original = copy(self.original)
        d.update({"y": "y"}, x="x")
        original.update({"y": "y"}, x="x")
        assert d == original

        d = RedisDict(self.original, key=self.key)
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
        d = RedisDict(self.original, key=self.key)
        original = copy(self.original)
        assert str(d) == str(original)

    def test___repr__(self):
        d = RedisDict(self.original, key=self.key)
        original = copy(self.original)
        assert repr(d) == repr(original)
