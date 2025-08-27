from abc import ABC

from buz.event.async_subscriber import AsyncSubscriber
from buz.event.meta_base_subscriber import MetaBaseSubscriber


class BaseAsyncSubscriber(AsyncSubscriber, MetaBaseSubscriber, ABC):
    pass
