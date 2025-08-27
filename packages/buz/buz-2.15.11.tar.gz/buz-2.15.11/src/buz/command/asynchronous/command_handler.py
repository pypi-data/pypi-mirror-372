from abc import abstractmethod
from typing import Type

from buz import Handler
from buz.command.command import Command


class CommandHandler(Handler):
    @classmethod
    @abstractmethod
    def handles(cls) -> Type[Command]:
        pass

    @abstractmethod
    async def handle(self, command: Command) -> None:
        pass
