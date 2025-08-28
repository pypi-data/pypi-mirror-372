import argparse
from typing import Type

from .command import Command
from .registry import CommandRegistry

__all__ = ["Command", "CommandRegistry"]

def __command_init__(argv=None) -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name, cmd_cls in CommandRegistry.all().items():
        if name != cmd_cls.NAME:
            continue

        cmd_cls.add_to_subparsers(subparsers)
    
    args = parser.parse_args(argv)

    cmd_cls: Type[Command] = getattr(args, "_command_cls", None)

    if cmd_cls is None:
        parser.error("no command selected")

    cmd = cmd_cls()

    cmd.run(args)
