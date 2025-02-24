# The original code that MathLamp originated was from a Lark template.
# Check it here -> https://github.com/lark-parser/lark/blob/08c91939876bd3b2e525441534df47e0fb25a4d1/examples/calc.py
import typer
from typing import Annotated
from typing import Optional

from lark import Lark, Transformer, v_args

import sys

from importlib import resources as impresources
from mathlamp import stdlamp

grammar_file = impresources.files(stdlamp) / "grammar.lark"
with grammar_file.open("r") as f:
    global grammar
    grammar = f.read()

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


def flatten(nested_list: list | tuple) -> list:
    """Flattens a list

    Args:
        nested_list (list | tuple): The list to be flattened

    Returns:
        list: The flattened list
    """
    result = []
    for item in nested_list:
        if isinstance(item, list | tuple):
            result.extend(flatten(item))  # Recursively flatten the sublist
        else:
            result.append(item)
    return result


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
        """Number value wrapper (`int` and `float`)"""
        try:
            return int(num)
        except ValueError:
            return float(num)

    def str(self, txt):
        """String value wrapper (`str`)"""
        return txt[1:-1]

    def add_item(self, *args):
        """List value wrapper (`list`)"""
        arg_list = [list(item) if isinstance(item, tuple) else item for item in args]
        return flatten(arg_list)

    def dict_pair(self, key, value):
        """Dictonary key: value pair wrapper"""
        return (key, value)
    
    def dict_items(self, pair1, pair2):
        """Dictonary items wrapper"""
        return (pair1, pair2)
    
    def dict_val(self, dict_val):
        flattned_dict = flatten(dict_val)
        result = dict(zip(flattned_dict[::2], flattned_dict[1::2]))
        return result


    def assign_var(self, name, value):
        """Variable assignement wrapper"""
        self.vars[name] = value
        return value

    def var(self, name):
        """Variable name call wrapper"""
        try:
            return self.vars[name]
        except KeyError:
            raise InvalidVariable(name, self.file)

    def out(self, value):
        """Out function"""
        print(value)


# Command definition
@app.command()
def main(
    file: Annotated[Optional[str], typer.Argument()] = "REPL",
    repl: Annotated[
        str, typer.Option("--repl", "-r", help="Pass a MathLamp expression to the repl")
    ] = "",
):
    sys.excepthook = lamp_error_hook
    calc_parser = Lark(grammar, parser="lalr", transformer=CalculateTree(file))
    calc = calc_parser.parse
    if repl:
        print(calc(repl))
        exit(0)
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
