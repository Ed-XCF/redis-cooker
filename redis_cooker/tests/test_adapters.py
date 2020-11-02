import enum
from typing import List

import pytest
from pydantic import BaseModel

from ..collections import *
from ..clients import *

set_connection_url('redis://:@127.0.0.1:6379/15')
client = current_redis_client()


class Sex(str, enum.Enum):
    MALE = 'male'
    FEMALE = 'female'


class Person(BaseModel):
    name: str
    age: int
    sex: Sex


class Group(BaseModel):
    name = "Group"
    members: List[Person]


class Persons(BaseModel):
    __root__: List[Person]


class TestPydantic:
    key = "Testing:Pydantic"

    def test_redis_dict(self):
        client.delete(self.key)
        original = {
            "group_a": {
                "members": [
                    {
                        "name": "A",
                        "age": 15,
                        "sex": Sex.MALE,
                    },
                    {
                        "name": "B",
                        "age": "16",
                        "sex": Sex.FEMALE,
                    },
                ]
            },
            "group_b": {
                "members": [
                    {
                        "name": "A",
                        "age": 15,
                        "sex": Sex.MALE,
                    },
                    {
                        "name": "B",
                        "age": "16",
                        "sex": Sex.FEMALE,
                    },
                ]
            },
        }
        d = RedisDict(self.key, init=original, schema=Group)
        for k, v in original.items():
            assert d[k] == Group(**v).dict()
        str(d)
        repr(d)

    def test_redis_list(self):
        client.delete(self.key)
        original = [
            {
                "name": "A",
                "age": 15,
                "sex": Sex.MALE,
            },
            {
                "name": "B",
                "age": "16",
                "sex": Sex.FEMALE,
            },
            {
                "name": "C",
                "age": "16",
                "sex": Sex.FEMALE,
            },
            {
                "name": "D",
                "age": "16",
                "sex": Sex.FEMALE,
            },
            {
                "name": "E",
                "age": "16",
                "sex": Sex.FEMALE,
            },
        ]
        l = RedisList(self.key, schema=Person)
        for index, value in enumerate(original):
            with pytest.raises(IndexError):
                l[index] = value
            l.append(value)
            assert l[index] == Person(**value).dict()

        assert l[1:-1] == [Person(**i).dict() for i in original[1:-1]]
        str(l)
        repr(l)

    def test_redis_mutable_set(self):
        client.delete(self.key)
        original = [
            {
                "name": "A",
                "age": 15,
                "sex": Sex.MALE,
            },
            {
                "name": "B",
                "age": "16",
                "sex": Sex.FEMALE,
            },
            {
                "name": "C",
                "age": "16",
                "sex": Sex.FEMALE,
            },
            {
                "name": "D",
                "age": "16",
                "sex": Sex.FEMALE,
            },
            {
                "name": "E",
                "age": "16",
                "sex": Sex.FEMALE,
            },
        ]

        s = RedisMutableSet(self.key, init=original, schema=Person)
        for i in original:
            temp = Person(**i).dict()
            assert temp in s
            s.add(i)
            assert temp in s
            s.remove(i)
            assert temp not in s

        client.delete(self.key)
        s = RedisMutableSet(self.key, init=original, schema=Persons)
        str(s)
        repr(s)
