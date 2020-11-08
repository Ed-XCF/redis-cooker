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
redis-cooker provide 8 datastructures in current version:
* collections: RedisMutableSet, RedisString, RedisList, RedisDict, RedisDeque, RedisDefaultDict
* queues: RedisQueue, RedisLifoQueue

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
