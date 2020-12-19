# redis-cooker
![GitHub](https://img.shields.io/github/license/Ed-XCF/redis-cooker)
[![Build Status](https://travis-ci.org/Ed-XCF/redis-cooker.svg?branch=master)](https://travis-ci.org/Ed-XCF/redis-cooker)
[![codecov](https://codecov.io/gh/Ed-XCF/redis-cooker/branch/master/graph/badge.svg?token=J3HnAigB4J)](undefined)
![PyPI](https://img.shields.io/pypi/v/redis-cooker)
## An redis python datastructures package
## Installation
To install redis-cooker, simply:

    $ pip install redis-cooker

or from source:

    $ python setup.py install
    
## Getting Started

    >>> from redis_cooker.clients import set_connection_url
    >>> from redis_cooker.collections import RedisList
    >>>
    >>> set_connection_url('redis://:@127.0.0.1:6379/15')
    >>> for i in RedisList("Testing:RedisList", init=['Hello', 'World']):
    >>>     print(i)
    Hello
    World
    
By default, all data will use the built-in json serializer.  

## Attention!
* If the key has existed in Redis, new object will connect to the existed key and ignore the "init" value.
* For complex operations, redis-cooker uses lua instead of python.

## Datastructures
redis-cooker provide 6 datastructures in current version:
* collections: RedisMutableSet, RedisString, RedisList, RedisDict, RedisDeque, RedisDefaultDict
* others: ABNTest

## Integration with Pydantic

    >>> from typing import List
    >>>
    >>> from pydantic import BaseModel
    >>> from redis_cooker.clients import set_connection_url
    >>> from redis_cooker.collections import RedisList
    >>>
    >>> set_connection_url('redis://:@127.0.0.1:6379/15')
    >>>
    >>>
    >>> class Person(BaseModel):
            name: str
            age: int
    >>>
    >>>
    >>> data = [{"name": "A", "age": 15},{"name": "B", "age": "16"}]
    >>> for i in RedisList("Testing:Pydantic", init=data, schema=Person):
    >>>     print(i)
    {'name': 'A', 'age': 15}
    {'name': 'B', 'age': '16'}

## Integration with DRF Serializer 

    >>> from typing import List
    >>>
    >>> from rest_framework import serializers
    >>> from redis_cooker.clients import set_connection_url
    >>> from redis_cooker.collections import RedisList
    >>>
    >>> set_connection_url('redis://:@127.0.0.1:6379/15')
    >>>
    >>>
    >>> class DRFPerson(serializers.Serializer):
            name = serializers.CharField()
            age = serializers.IntegerField()
    >>>
    >>>
    >>> data = [{"name": "A", "age": 15},{"name": "B", "age": "16"}]
    >>> for i in RedisList("Testing:DRF", init=data, schema=DRFPerson):
    >>>     print(i)
    OrderedDict([('name', 'A'), ('age', 15)])
    OrderedDict([('name', 'B'), ('age', 16)])

## Use ABNTest in your internal A/B Test

    >>> from redis_cooker.abn_test import ABNTest, Choice
    >>> from redis_cooker.clients import current_redis_client, set_connection_url
    >>>
    >>> set_connection_url('redis://:@127.0.0.1:6379/15')
    >>> client = current_redis_client()
    >>>
    >>> topic = "lead comment"
    >>> choices = [Choice(name="A", value=5), Choice(name="B", value=5), Choice(name="C", value=2)]
    >>> abn_test = ABNTest(topic, choices)
    >>> choice = abn_test.fetch()
