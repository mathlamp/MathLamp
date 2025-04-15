# The original code that MathLamp originated was from a Lark template.
# Check it here -> https://github.com/lark-parser/lark/blob/08c91939876bd3b2e525441534df47e0fb25a4d1/examples/calc.py
import typer
from typing import Annotated
from typing import Optional

from lark import Lark, v_args
from lark.visitors import Interpreter

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

class CalculateTree(Interpreter):
    def __init__(self, file: str = "REPL"):
        super().__init__()
        self.file = file
        self.vars = {}

    def start(self, tree):
        self.visit_children(tree)

    def out(self, tree):
        if self.file == "REPL":
            return self.visit_children(tree)[0]
        else:
            print(self.visit_children(tree)[0])
    
    def add(self, tree):
        data = self.visit_children(tree)
        return data[0] + data[1]

    def number(self, tree):
        from re import match
        val =  tree.children[0].value
        if match(r'[0-9]+\.[0-9]+', val):
            return float(val)
        else:
            return int(val)
    
    def str(self, tree):
        return tree.children[0].value

# Command definition
@app.command()
def main(
    file: Annotated[Optional[str], typer.Argument()] = "REPL",
    repl: Annotated[
        str, typer.Option("--repl", "-r", help="Pass a MathLamp expression to the repl")
    ] = "",
):
    sys.excepthook = lamp_error_hook
    calc_parser = Lark(grammar, parser="lalr")
    if repl:
        tree = calc_parser.parse(repl)
        print(CalculateTree().visit(tree))
        exit(0)
    if file == "REPL":
        while True:
            try:
                s = input("> ")
            except EOFError:
                break
            tree = calc_parser.parse(s)
            print(CalculateTree().visit(tree))
    else:
        try:
            with open(file, "r") as f:
                code = f.read()
                tree = calc_parser.parse(code)
                CalculateTree(file).visit(tree)
                
        except FileNotFoundError:
            raise MissingFile(file)


if __name__ == "__main__":
    app()
