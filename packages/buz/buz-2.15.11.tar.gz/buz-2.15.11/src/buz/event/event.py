from dataclasses import dataclass

from buz import Message


@dataclass(frozen=True)
class Event(Message):
    @classmethod
    def fqn(cls) -> str:
        return f"event.{super().fqn()}"
