# cmdplug
cmdplug is a lightweight Python package that makes it easy to build command-line interfaces using argparse.

# Usage
Create a command class by inheriting from Command provided by cmdplug.
```
# example: calculator.py
from argparse import ArgumentParser, Namespace
from cmdplug import Command

class Calculator(Command):
    NAME="calculator"
    HELP="for example"

    @classmethod
    def add_arguments(cls, parser: ArgumentParser):
        parser.add_argument("-x", "--x", help="x variable", type=int)
        parser.add_argument("-y", "--y", help="y variable", type=int)

    def run(self, args: Namespace) -> int:
        x, y = args.x, args.y
        print(f"x({x}) + y({y}) = {args.x + args.y}")
        return 0
```

Then, in your main entry point, simply import the command class and call __command_init__().
```
from exmaple import Calculator

from cmdplug import __command_init__

if __name__ == "__main__":
    __command_init__()
```

# Developer’s Note
I hope you enjoy building your own CLI tools with cmdplug and have fun coding!
