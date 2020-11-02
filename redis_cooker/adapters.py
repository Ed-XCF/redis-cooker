import json
from abc import ABCMeta, abstractmethod
from typing import Any


class BaseAdapter(metaclass=ABCMeta):
    def __init__(self, adaptee: Any):
        self.adaptee = adaptee

    @abstractmethod
    def loads(self, data: bytes) -> Any:
        pass

    @abstractmethod
    def dumps(self, data: Any) -> str:
        pass


class PydanticAdapter(BaseAdapter):
    def loads(self, data: bytes) -> Any:
        return self.adaptee.parse_raw(data).dict()

    def dumps(self, data: Any) -> str:
        if self.adaptee.__custom_root_type__:
            data = {"__root__": data}

        if self.adaptee.Config.orm_mode:
            factory = self.adaptee.from_orm
        else:
            factory = self.adaptee.parse_obj

        return factory(data).json()


class DRFAdapter(BaseAdapter):
    def loads(self, data: bytes) -> Any:
        serializer = self.adaptee(data=json.loads(data))
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def dumps(self, data: Any) -> str:
        return self.adaptee(data).data
