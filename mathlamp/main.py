# The original code that MathLamp originated was from a Lark template.
# Check it here -> https://github.com/lark-parser/lark/blob/08c91939876bd3b2e525441534df47e0fb25a4d1/examples/calc.py
import typer
import sys
from lark import Lark, Transformer, v_args
from typing import Annotated
from typing import Optional

from mathlamp.grammar import grammar

app = typer.Typer(pretty_exceptions_enable=False)


# Error definitions
class LampError(Exception):

    def __init__(self, msg: str, file: str):
        """Base class for MathLamp errors

        Args:
            msg (str): The error's message
            file (str): The file that the error ocurred
        """
        self.msg = f"On file: {file}\nERROR ({type(self).__name__}): {msg}"
        super().__init__(self.msg)


class InvalidVariable(LampError):

    def __init__(self, var: str, file: str):
        """Error for a invalid variable

        Called when a invalid variable is found by the interpreter.
        (Ex: Missing variables)

        Args:
            var (str): The variable's name
            file (str): The file that the error ocurred
        """
        self.msg = "Variable not found: " + var
        super().__init__(self.msg, file)


class MissingFile(LampError):

    def __init__(self, file: str):
        """Error for a missing file

        Called when the `lamp` command looks for a non-existent file

        Args:
            file (str): The missing file
        """
        self.msg = f"File {file} was not found"
        super().__init__(self.msg, file)


# Error hook
def lamp_error_hook(exc_type, exc_value, exc_tb):
    if issubclass(exc_type, LampError):
        print(exc_value, file=sys.stderr)
    else:
        sys.__excepthook__(exc_type, exc_value, exc_tb)


# Transformer class
@v_args(inline=True)
class CalculateTree(Transformer):
    from operator import add, sub, mul, truediv as div, neg, mod, pow
    from math import sqrt

    def __init__(self, file: str):
        super().__init__()
        self.file = file
        self.vars = {}

    def number(self, num):
        try:
            return int(num)
        except ValueError:
            return float(num)

    def assign_var(self, name, value):
        self.vars[name] = value
        return value

    def var(self, name):
        try:
            return self.vars[name]
        except KeyError:
            raise InvalidVariable(name, self.file)

    def out(self, value):
        print(value)


# Command definition
@app.command()
def main(file: Annotated[Optional[str], typer.Argument()] = "REPL"):
    sys.excepthook = lamp_error_hook
    calc_parser = Lark(grammar, parser="lalr", transformer=CalculateTree(file))
    calc = calc_parser.parse
    if file == "REPL":
        while True:
            try:
                s = input("> ")
            except EOFError:
                break
            print(calc(s))
    else:
        try:
            with open(file, "r") as f:
                code = f.readlines()
                for line in code:
                    line = line.rstrip()
                    calc(line)
        except FileNotFoundError:
            raise MissingFile(file)


if __name__ == "__main__":
    app()
