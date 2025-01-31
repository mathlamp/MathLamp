# The original code that MathLamp originated was from a Lark template.
# Check it here -> https://github.com/lark-parser/lark/blob/08c91939876bd3b2e525441534df47e0fb25a4d1/examples/calc.py
import typer
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


# Transformer class
@v_args(inline=True)  # Affects the signatures of the methods
class CalculateTree(Transformer):
    from operator import add, sub, mul, truediv as div, neg, mod, pow
    from math import sqrt

    def __init__(self):
        super().__init__()
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
            raise Exception("ERROR: Variable not found: %s" % name)

    def out(self, value):
        print(value)


calc_parser = Lark(grammar, parser='lalr', transformer=CalculateTree())
calc = calc_parser.parse


# Command definition
@app.command()
def main(file: Annotated[Optional[str], typer.Argument()] = None):
    if not file:
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
            print(f"ERROR: File {file} was not found,\ntry checking if you included the file extension")


if __name__ == "__main__":
    app()
