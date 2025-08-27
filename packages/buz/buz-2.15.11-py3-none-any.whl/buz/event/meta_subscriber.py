from abc import ABC, abstractmethod
from typing import Awaitable, Type, Union

from buz import Handler
from buz.event import Event


class MetaSubscriber(Handler, ABC):
    @abstractmethod
    def consume(self, event: Event) -> Union[None, Awaitable[None]]:
        pass

    @classmethod
    @abstractmethod
    def handles(cls) -> Type[Event]:
        pass
