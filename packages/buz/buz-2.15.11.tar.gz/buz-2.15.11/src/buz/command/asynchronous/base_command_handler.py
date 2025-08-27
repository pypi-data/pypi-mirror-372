from typing import Type, get_type_hints, Any

from buz.command import Command
from buz.command.asynchronous.command_handler import CommandHandler


class BaseCommandHandler(CommandHandler):
    @classmethod
    def fqn(cls) -> str:
        return f"command_handler.{cls.__module__}.{cls.__name__}"

    @classmethod
    def handles(cls) -> Type[Command]:
        handle_types = get_type_hints(cls.handle)

        if "command" not in handle_types:
            raise TypeError(
                f"The method 'handle' in '{cls.fqn()}' doesn't have a parameter named 'command'. Found parameters: {cls.__get_method_parameter_names(handle_types)}"
            )

        if not issubclass(handle_types["command"], Command):
            raise TypeError(f"The parameter 'command' in '{cls.fqn()}.handle' is not a 'buz.command.Command' subclass")

        return handle_types["command"]

    @classmethod
    def __get_method_parameter_names(cls, handle_types: dict[str, Any]) -> list[str]:
        handle_types_copy: dict = handle_types.copy()
        handle_types_copy.pop("return", None)
        return list(handle_types_copy.keys())
