from argparse import _SubParsersAction, ArgumentParser
from abc import ABC, abstractmethod
from typing import List

class Command(ABC):
    NAME: str = ""
    HELP: str = ""
    ALIASES: List[str] = []

    def __init_subclass__(cls, abstract: bool = False, **kwargs):
        super().__init_subclass__(**kwargs)

        if abstract:
            return

        if cls.run is Command.run:
            return
        
        from .registry import CommandRegistry
        CommandRegistry.register(cls)
    
    @classmethod
    def add_to_subparsers(cls, subparsers: _SubParsersAction) -> _SubParsersAction:
        parser = subparsers.add_parser(
            cls.NAME,
            help=cls.HELP or cls.__doc__,
            aliases=cls.ALIASES,
            description=(cls.__doc__ or cls.HELP or cls.NAME)
        )

        cls.add_arguments(parser)
        parser.set_defaults(_command_cls=cls)

        return parser
    
    @classmethod
    def add_arguments(cls, parser: ArgumentParser) -> None:
        return
    
    @abstractmethod
    def run(self, args) -> int:
        pass
