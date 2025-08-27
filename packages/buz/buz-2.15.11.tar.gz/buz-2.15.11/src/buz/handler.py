from abc import ABC, abstractmethod
from typing import Type

from buz import Message


class Handler(ABC):
    @classmethod
    @abstractmethod
    def handles(cls) -> Type[Message]:
        pass

    @classmethod
    @abstractmethod
    def fqn(cls) -> str:
        pass
