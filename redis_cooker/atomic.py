import functools
from typing import Callable

from redis.client import Script

__all__ = ["run_as_lua"]


def run_as_lua(parameter_converter: Callable) -> Callable:
    def create_lua_script(func: Callable) -> Callable:
        @functools.wraps(func)
        def __inner(self, *args, **kwargs) -> None:
            lua_attr: str = "_lua_"
            try:
                script: Script = getattr(func, lua_attr)
            except AttributeError:
                script: Script = self.redis.register_script(func.__doc__)
                setattr(func, lua_attr, script)

            return script(keys=[self.key], args=parameter_converter(*args, **kwargs))

        return __inner

    return create_lua_script
