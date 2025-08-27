from abc import ABC
from buz.event import Subscriber
from buz.event.meta_base_subscriber import MetaBaseSubscriber


class BaseSubscriber(Subscriber, MetaBaseSubscriber, ABC):
    pass
