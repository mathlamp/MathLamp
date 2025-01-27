# The original code that MathLamp originated was from a Lark template.
# Check it here -> https://github.com/lark-parser/lark/blob/08c91939876bd3b2e525441534df47e0fb25a4d1/examples/calc.py
import typer
from lark import Lark, Transformer, v_args
from typing import Annotated
from typing import Optional
from rich.console import Console

f = open("grammar.lark", "r")
grammar = f.read()
f.close()

console = Console()
app = typer.Typer(pretty_exceptions_enable=False)

@v_args(inline=True)    # Affects the signatures of the methods
class CalculateTree(Transformer):
    from operator import add, sub, mul, truediv as div, neg, mod, pow
    from math import sqrt
    number = float

    def __init__(self):
        super().__init__()
        self.vars = {}

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

@app.command()
def main(file: Annotated[Optional[str], typer.Argument()]=None):
    if not file:
        while True:
            try:
                s = input('> ')
            except EOFError:
                break
            print(calc(s))
    else:
        try:
            with open(file,"r") as f:
                code = f.readlines()
                for line in code:
                    line = line.rstrip()
                    calc(line)
        except FileNotFoundError:
            console.print(f"ERROR: File {file} was not found,\ntry checking if you included the file extension", style="bold red")

if __name__ == "__main__":
    app()