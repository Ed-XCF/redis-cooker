# redis-cooker
![GitHub](https://img.shields.io/github/license/Ed-XCF/redis-cooker)
[![Build Status](https://travis-ci.org/Ed-XCF/redis-cooker.svg?branch=master)](https://travis-ci.org/Ed-XCF/redis-cooker)
[![codecov](https://codecov.io/gh/Ed-XCF/redis-cooker/branch/master/graph/badge.svg?token=J3HnAigB4J)](undefined)
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
redis-cooker tested with Python 3.6 - 3.8.
