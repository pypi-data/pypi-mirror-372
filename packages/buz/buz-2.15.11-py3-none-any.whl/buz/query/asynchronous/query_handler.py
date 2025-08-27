from abc import abstractmethod
from typing import Type

from buz import Handler
from buz.query import Query, QueryResponse


class QueryHandler(Handler):
    @classmethod
    @abstractmethod
    def handles(cls) -> Type[Query]:
        pass

    @abstractmethod
    async def handle(self, query: Query) -> QueryResponse:
        pass
