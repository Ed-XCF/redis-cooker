# redis-cooker
## An redis operation proxy package
## Installation
To install redis-cooker, simply:

    $ pip install redis-cooker

or from source:

    $ python setup.py install
    
## Getting Started

    >>> from redis_cooker.collections import RedisDict
    >>> data = RedisDict({"a": 1, "b":2}, key="first:RedisDict")
    >>> for v in data.values(): print(v)

By default, all responses are returned as `str`.

## Python Version Support
redis-cooker supports Python 3.6.
