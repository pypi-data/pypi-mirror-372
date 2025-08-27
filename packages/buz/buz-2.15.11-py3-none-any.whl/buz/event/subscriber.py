from abc import ABC, abstractmethod

from buz.event import Event
from buz.event.meta_subscriber import MetaSubscriber


class Subscriber(MetaSubscriber, ABC):
    @abstractmethod
    def consume(self, event: Event) -> None:
        pass
