import enum
from typing import List

from pydantic import BaseModel

from ..collections import RedisDict
from ..clients import *

set_connection_url('redis://:@127.0.0.1:16379/15')
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


class TestPydantic:
    key = "Testing:RedisDict"

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
        d = RedisDict(self.key, init=original, model=Group)
        for k, v in original.items():
            assert d[k] == Group(**v)
