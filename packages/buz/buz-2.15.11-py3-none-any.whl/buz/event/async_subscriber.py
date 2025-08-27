from abc import ABC, abstractmethod

from buz.event import Event
from buz.event.meta_subscriber import MetaSubscriber


class AsyncSubscriber(MetaSubscriber, ABC):
    @abstractmethod
    async def consume(self, event: Event) -> None:
        pass
