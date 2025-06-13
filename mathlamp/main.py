# The original code that MathLamp originated was from a Lark template.
# Check it here -> https://github.com/lark-parser/lark/blob/08c91939876bd3b2e525441534df47e0fb25a4d1/examples/calc.py
import typer
from typing import Annotated
from typing import Optional

from lark import Lark
from lark.visitors import Interpreter

from rich.console import Console
import rich

console = Console()

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

class ArgumentError(LampError):
    def __init__(self, num: int, exp: int, func: str, file: str):
        """Error for a invalid number of arguments

        Args:
            num (int): The provided number of args
            exp (int): The expected number of args 
            file (str): The file that the error ocurred
        """
        self.msg = f"Function {func} recived {num} args, but expected {exp} args"
        super().__init__(self.msg, file)

# Error hook
def lamp_error_hook(exc_type, exc_value, exc_tb):
    if issubclass(exc_type, LampError):
        rich.print(f"[bold red]{exc_value}[/bold red]", file=sys.stderr)
    else:
        sys.__excepthook__(exc_type, exc_value, exc_tb)


def flatten(nested_list: list) -> list:
    """Flattens a list

    Args:
        nested_list (list): The list to be flattened

    Returns:
        list: The flattened list
    """
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten(item))  # Recursively flatten the sublist
        else:
            result.append(item)
    return result


class CalculateTree(Interpreter):
    def __init__(self, file: str = "REPL"):
        super().__init__()
        self.file = file
        self.vars = {}
        self.funcs = []

    def start(self, tree):
        self.visit_children(tree)

    def out(self, tree):
        """out() function"""
        if self.file == "REPL":
            return self.visit_children(tree)[0]
        else:
            print(self.visit_children(tree)[0])

    def pow(self, tree):
        """pow() function"""
        data = self.visit_children(tree)
        return data[0] ** data[1]

    def sqrt(self, tree):
        """sqrt() function"""
        from math import sqrt

        data = self.visit_children(tree)
        val = sqrt(data[0])
        if val.is_integer():
            return int(val)
        else:
            return val

    def var(self, tree):
        name = tree.children[0].value
        return self.vars[name]

    def assign_var(self, tree):
        name = tree.children[0].value
        val = self.visit_children(tree)[1]
        self.vars[name] = val

    def add(self, tree):
        data = self.visit_children(tree)
        return data[0] + data[1]

    def sub(self, tree):
        data = self.visit_children(tree)
        return data[0] - data[1]

    def mul(self, tree):
        data = self.visit_children(tree)
        return data[0] * data[1]

    def div(self, tree):
        data = self.visit_children(tree)
        val = data[0] / data[1]
        if val.is_integer():
            return int(val)
        else:
            return val

    def mod(self, tree):
        data = self.visit_children(tree)
        return data[0] % data[1]

    def number(self, tree):
        from re import match

        val = tree.children[0].value
        if match(r"[0-9]+\.[0-9]+", val):
            return float(val)
        else:
            return int(val)

    def str(self, tree):
        return tree.children[0].value[1:-1]

    def empty_list(self, tree):
        return []

    def single_list(self, tree):
        data = self.visit_children(tree)
        return [data[0]]

    def add_item(self, tree):
        data = self.visit_children(tree)
        val = [data[0], data[1]]
        return flatten(val)

    def empty_dict(self, tree):
        return {}

    def dict_pair(self, tree):
        data = self.visit_children(tree)
        return (data[0], data[1])

    def dict_items(self, tree):
        data = self.visit_children(tree)
        return flatten(data)

    def dict_val(self, tree):
        data = self.visit_children(tree)
        if isinstance(data[0], list):
            return dict(data[0])
        else:
            return dict(data)

    def true(self, tree):
        return True

    def false(self, tree):
        return False

    def if_block(self, tree):
        data = self.visit(tree.children[0])
        if data:
            out = self.visit(tree.children[1])
            if not out == None:
                return out

    def eq(self, tree):
        from operator import eq

        data = self.visit_children(tree)
        return eq(data[0], data[1])

    def ne(self, tree):
        from operator import ne

        data = self.visit_children(tree)
        return ne(data[0], data[1])

    def lt(self, tree):
        from operator import lt

        data = self.visit_children(tree)
        return lt(data[0], data[1])

    def le(self, tree):
        from operator import le

        data = self.visit_children(tree)
        return le(data[0], data[1])

    def gt(self, tree):
        from operator import gt

        data = self.visit_children(tree)
        return gt(data[0], data[1])

    def ge(self, tree):
        from operator import ge

        data = self.visit_children(tree)
        return ge(data[0], data[1])

    def repeat_block(self, tree):
        data = self.visit(tree.children[0])
        for _ in range(data):
            out = self.visit(tree.children[1])
            if type(out).__name__ == "list":
                for i in flatten(out):
                    print(i)
            elif not out == None:
                print(out) 

    def for_block(self, tree):
        name = tree.children[0].children[0].value
        num = self.visit(tree.children[1])
        for i in num:
            self.vars[name] = i
            out = self.visit(tree.children[2])
            if self.file == "REPL":
                if type(out).__name__ == "list":
                    for i in flatten(out):
                        print(i)
                elif not out == None:
                    print(out)

    def func_block(self, tree):
        name = tree.children[0].value
        if tree.children[1].data == "params":
            params = self.visit(tree.children[1])
            block = tree.children[2]
        else:
            params = []
            block = tree.children[1]
        func = {"name": name, "params": params, "block": block}
        self.funcs.append(func)

    def default_func(self, tree):
        name = tree.children[0].value
        try:
            args = self.visit(tree.children[1])
        except IndexError:
            args = []
        func = next(filter(lambda x: x["name"] == name, self.funcs), None)
        if not len(args) == len(func["params"]):
            raise ArgumentError(len(args), len(func["params"]), func["name"], self.file)
        if not len(args) == 0:
            for i, arg in enumerate(args):
                self.vars[func["params"][i]] = arg
        result = self.visit(func["block"])
        if self.file == "REPL":
                if type(result).__name__ == "list":
                    for i in flatten(result):
                        print(i)
                elif not result == None:
                    print(result)
        

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
        console.print(
            "[yellow]The MathLamp REPL[/yellow]\nVersion [bold cyan]1.2.0-dev[/bold cyan] [bold red]=DEV TESTING="
        )
        calc = CalculateTree()
        while True:
            try:
                s = input("> ")
            except EOFError:
                break
            tree = calc_parser.parse(s)
            val = calc.visit(tree)
            if not val == None:
                print(val)
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
