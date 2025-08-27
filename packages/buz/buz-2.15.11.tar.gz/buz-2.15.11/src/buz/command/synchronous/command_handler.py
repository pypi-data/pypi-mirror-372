from abc import abstractmethod
from typing import Type

from buz import Handler
from buz.command import Command


class CommandHandler(Handler):
    @classmethod
    @abstractmethod
    def handles(cls) -> Type[Command]:
        pass

    @abstractmethod
    def handle(self, command: Command) -> None:
        pass
