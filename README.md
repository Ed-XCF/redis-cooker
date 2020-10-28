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

    >>> from redis_cooker.collections import RedisDict
    >>> data = RedisDict("first:RedisDict", init={"a": 1, "b":2})
    >>> for v in data.values(): print(v)

By default, all responses are returned as `str`.

## Python Version Support
redis-cooker tested with Python 3.6 - 3.8.
