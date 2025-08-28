from typing import Dict, Type

class CommandRegistry:
    _commands: Dict[str, Type["Command"]] = {}

    @classmethod
    def register(cls, cmd_cls: Type["Command"]) -> None:
        name = getattr(cmd_cls, "NAME", "") or ""

        if not name:
            raise ValueError(f"{cmd_cls.__name__}.NAME must be set")
        
        if name in cls._commands:
            raise ValueError(f"Duplicate command name: {name}")
        
        cls._commands[name] = cmd_cls 

    @classmethod
    def all(cls) -> Dict[str, Type["Command"]]:
        return dict(cls._commands)