from abc import ABC
from typing import Type, get_type_hints

from buz.event import Event
from buz.event.meta_subscriber import MetaSubscriber


class MetaBaseSubscriber(MetaSubscriber, ABC):
    @classmethod
    def fqn(cls) -> str:
        return f"subscriber.{cls.__module__}.{cls.__name__}"

    @classmethod
    def handles(cls) -> Type[Event]:
        consume_types = get_type_hints(cls.consume)

        if "event" not in consume_types:
            raise TypeError("event parameter not found in consume method")

        if not issubclass(consume_types["event"], Event):
            raise TypeError("event parameter is not an buz.event.Event subclass")

        return consume_types["event"]
