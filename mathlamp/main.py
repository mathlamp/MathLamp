# The original code that MathLamp originated was from a Lark template.
# Check it here -> https://github.com/lark-parser/lark/blob/08c91939876bd3b2e525441534df47e0fb25a4d1/examples/calc.py
import typer
import sys
from lark import Lark, Transformer, v_args
from typing import Annotated
from typing import Optional

grammar = r"""
?start: sum
          | NAME "=" sum    -> assign_var

    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div
        | product "%" atom  -> mod

    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | NAME             -> var
         | "(" sum ")"
         | "out" "[" sum "]" -> out
         | "sqrt" "[" sum "]" -> sqrt
         | "pow" "[" sum "," sum "]" -> pow

    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS_INLINE

    %ignore WS_INLINE
    %ignore /\/\/[^\n]*/
"""

app = typer.Typer(pretty_exceptions_enable=False)


# Error definitions
class LampError(Exception):
    """Base class for MathLamp errors"""

    def __init__(self, msg: str, file: str):
        self.msg = f"On file: {file}\nERROR ({type(self).__name__}): {msg}"
        super().__init__(self.msg)

class InvalidVariable(LampError):
    """Error for a missing variable"""

    def __init__(self, var: str, file: str):
        self.msg = "Variable not found: " + var
        super().__init__(self.msg, file)

class MissingFile(LampError):
    """Error for an invalid file path"""
    def __init__(self, file: str):
        self.file = file
        self.msg = f"File {self.file} was not found"
        super().__init__(self.msg, self.file)

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
    calc_parser = Lark(grammar, parser='lalr', transformer=CalculateTree(file))
    calc = calc_parser.parse
    if file == "REPL":
        while True:
            try:
                s = input('> ')
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
