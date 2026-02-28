# The original code that MathLamp originated was from a Lark template.
# Check it here -> https://github.com/lark-parser/lark/blob/08c91939876bd3b2e525441534df47e0fb25a4d1/examples/calc.py
import typer
from typing import Annotated
from typing import Optional

from lark import Lark
from lark.visitors import Interpreter
from lark.exceptions import UnexpectedToken

from rich.console import Console
import rich

console = Console()

import sys
from os import getcwd

from importlib import resources as impresources
import importlib.util
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

		Called when a file waas not found

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


class InvalidFunction(LampError):
	def __init__(self, func: str, file: str):
		"""Error for a invalid function
		(Ex: calling an undefined function)

		Args:
			func (str): The name of the function
			file (str): The file that the error ocurred
		"""
		self.msg = f"The function {func} is not defined"
		super().__init__(self.msg, file)

class InvalidProperty(LampError):
	def __init__(self, prop: str, struct: str, file: str):
		"""Error for a invalid struct property
		(Ex: reading a property that doesn't exist)

		Args:
			prop (str): The invalid property
			struct (str): The struct
			file (str): The file that the error ocurred
		"""
		self.msg = f"The property {prop} does not exist on struct {struct}"
		super().__init__(self.msg, file)
		
class InvalidPackageProvider(LampError):
	def __init__(self, provid: str, file: str):
		"""Error for an invalid package provider
		(Ex: `import baz:example`)

		Args:
			provid (str): The invalid package provider
			file (str): The file that the error ocurred
		"""
		self.msg = f"The package provider {provid} does not exist"
		super().__init__(self.msg, file)

# Error hook
def lamp_error_hook(exc_type, exc_value, exc_tb):
	if issubclass(exc_type, LampError):
		rich.print(f"[bold red]{exc_value}[/bold red]", file=sys.stderr)
		exit(1)
	if exc_type == UnexpectedToken:
		parser = exc_value.interactive_parser
		token = exc_value.token
		line = token.line
		column = token.column
		rich.print(
			f"[bold red]ERROR (InvalidSyntax) At line {line}, column {column}:\n Expected one of: {parser.accepts()}[/bold red]",
			file=sys.stderr,
		)
		exit(1)
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
		self.structs = []

	def start(self, tree):
		self.visit_children(tree)

	def out(self, tree):
		"""out() function
		
		Ex. `out("Hello World!")`
		"""
		if self.file == "REPL":
			return self.visit_children(tree)[0]
		else:
			print(self.visit_children(tree)[0])

	def pow(self, tree):
		"""pow() function
		
		Ex. `pow(2,2) // 4`
		"""
		data = self.visit_children(tree)
		return data[0] ** data[1]

	def sqrt(self, tree):
		"""sqrt() function
		
		Ex. `sqrt(25) // 5`
		"""
		from math import sqrt

		data = self.visit_children(tree)
		val = sqrt(data[0])
		if val.is_integer():
			return int(val)
		else:
			return val

	def var(self, tree):
		"""Variable reference
		
		Ex. `foo = 1
		out(foo) // 1`
		"""
		name = tree.children[0].value
		try:
			return self.vars[name]
		except KeyError:
			raise InvalidVariable(name, self.file)

	def assign_var(self, tree):
		"""Variable assignment
		
		Ex. `bar = 123`
		"""
		name = tree.children[0].value
		val = self.visit_children(tree)[1]
		if isinstance(val, dict) and "members" in val:
			tempStruct = val | {"values": {}}
			for member in val["members"]:
				tempStruct[member] = None
			val = tempStruct
		self.vars[name] = val

	def add(self, tree):
		"""Addition operator
		
		Ex. `1 + 1`
		"""
		data = self.visit_children(tree)
		return data[0] + data[1]

	def sub(self, tree):
		"""Subtraction operation
		
		Ex. `2 - 1`
		"""
		data = self.visit_children(tree)
		return data[0] - data[1]

	def mul(self, tree):
		"""Multiplication operation
		
		Ex. `2 * 2`
		"""
		data = self.visit_children(tree)
		return data[0] * data[1]

	def div(self, tree):
		"""Division operation
		
		Ex. `11 / 4`
		"""
		data = self.visit_children(tree)
		val = data[0] / data[1]
		if val.is_integer():
			return int(val)
		else:
			return val

	def mod(self, tree):
		"""Modulus operation
		
		Ex. `11 % 4`
		"""
		data = self.visit_children(tree)
		return data[0] % data[1]

	def number(self, tree):
		"""Number type
		
		Ex. `123`
		"""
		from re import match

		val = tree.children[0].value
		if match(r"[0-9]+\.[0-9]+", val):
			return float(val)
		else:
			return int(val)

	def str(self, tree):
		"""String type
		
		Ex. `"Hello World"`
		"""
		return tree.children[0].value[1:-1]

	def empty_list(self, tree):
		"""Empty list
		
		Ex. `[]`
		"""
		return []

	def single_list(self, tree):
		"""List with a single item
		
		Ex. `[123]`
		"""
		data = self.visit_children(tree)
		return [data[0]]

	def add_item(self, tree):
		"""List item pair

		Can be nested
		
		Ex. `[123, "baz"]`
		"""
		data = self.visit_children(tree)
		val = [data[0], data[1]]
		return flatten(val)

	def empty_dict(self, tree):
		"""Empty dictionary
		
		Ex. `{}`
		"""
		return {}

	def dict_pair(self, tree):
		"""Dictionary key-item pair
		
		Ex. `{"foo": "bar"}`
		"""
		data = self.visit_children(tree)
		return (data[0], data[1])

	def dict_items(self, tree):
		"""Two dict_pair container
		
		Can be nested

		Ex. `{"foo": "bar", "num": 123}`
		"""
		data = self.visit_children(tree)
		return flatten(data)

	def dict_val(self, tree):
		"""Dictionary value
		
		Ex. `{"abc": "def"}`
		"""
		data = self.visit_children(tree)
		if isinstance(data[0], list):
			return dict(data[0])
		else:
			return dict(data)

	def true(self, tree):
		"""True boolean value
		
		Ex. `true`
		"""
		return True

	def false(self, tree):
		"""False boolean value
		
		Ex. `false`
		"""
		return False

	def if_block(self, tree):
		"""If block
		
		Ex. `if (true) {
    			out("hello")
			}`
		"""
		data = self.visit(tree.children[0])
		if data:
			out = self.visit(tree.children[1])
			if not out == None:
				return out

	def eq(self, tree):
		"""Equal operator
		
		Ex. `12 == 12`
		"""
		from operator import eq

		data = self.visit_children(tree)
		return eq(data[0], data[1])

	def ne(self, tree):
		"""Not equal operator
		
		Ex. `4 != 2`
		"""
		from operator import ne

		data = self.visit_children(tree)
		return ne(data[0], data[1])

	def lt(self, tree):
		"""Less than operator
		
		Ex. `4 < 7`
		"""
		from operator import lt

		data = self.visit_children(tree)
		return lt(data[0], data[1])

	def le(self, tree):
		"""Less than or equal operator
		
		Ex. `34 <= 50`
		"""
		from operator import le

		data = self.visit_children(tree)
		return le(data[0], data[1])

	def gt(self, tree):
		"""Greater than operator
		
		Ex. `12 > 5`
		"""
		from operator import gt

		data = self.visit_children(tree)
		return gt(data[0], data[1])

	def ge(self, tree):
		"""Greater than or equal operator
		
		Ex. `23 >= 12`
		"""
		from operator import ge

		data = self.visit_children(tree)
		return ge(data[0], data[1])

	def repeat_block(self, tree):
		"""Repeat a block x times
		
		Ex. `repeat (x) {
				out("hello")
			}`
		"""
		data = self.visit(tree.children[0])
		for _ in range(data):
			out = self.visit(tree.children[1])
			if type(out).__name__ == "list":
				for i in flatten(out):
					print(i)
			elif not out == None:
				print(out)

	def for_block(self, tree):
		"""Iterate over a list
		
		Ex. `items = [1, 2, 3]
		for (item in items) {
			out(item)
		}
		`
		"""
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
		"""Function definition
		
		func hello() {
			"hello"
		}
		"""
		name = tree.children[0].value
		if tree.children[1].data == "params":
			params = self.visit(tree.children[1])
			block = tree.children[2]
		else:
			params = []
			block = tree.children[1]
		func = {"name": name, "params": params, "block": block, "namespace": self.file, "module": self.file, "lang": "lamp"}
		self.funcs.append(func)

	def default_func(self, tree):
		"""Function call
		
		Ex. `hello()`
		"""
		from pathlib import Path

		name = tree.children[0].value
		try:
			args = self.visit(tree.children[1])
		except IndexError:
			args = []
		func = next(
			filter(
				lambda x: x["name"] == name and x["namespace"] == self.file, self.funcs
			),
			None,
		)
		if func is None:
			raise InvalidFunction(name, self.file)
		if not len(args) == len(func["params"]):
			raise ArgumentError(len(args), len(func["params"]), func["name"], self.file)
		if not len(args) == 0 and func["lang"] == "lamp":
			for i, arg in enumerate(args):
				self.vars[func["params"][i]] = arg
		if func["lang"] == "lamp":
			result = self.visit(func["block"])
		elif func["lang"] == "python":
			spec = importlib.util.spec_from_file_location(str(Path(func["module"]).stem), func["module"])
			extern = importlib.util.module_from_spec(spec)
			sys.modules[str(Path(func["module"]).stem)] = extern
			spec.loader.exec_module(extern)
			func_python = getattr(extern.LampExtern(), func["name"])
			result = func_python(*args)
		if type(result).__name__ == "list":
			for i in flatten(result):
				return i
		elif not result == None:
			return result
		if not len(args) == 0 and func["lang"] == "lamp":
			for i, arg in enumerate(args):
				self.vars.pop(func["params"][i])

	def namespace_func(self, tree):
		"""Namespaced function call
		
		Ex. `mylib:hello()`
		"""
		from pathlib import Path

		name = tree.children[1].value
		namespace = tree.children[0].value
		try:
			args = self.visit(tree.children[2])
		except IndexError:
			args = []
		func = next(
			filter(
				lambda x: x["name"] == name and x["namespace"] == namespace, self.funcs
			),
			None,
		)
		if func is None:
			raise InvalidFunction(namespace + "." + name, self.file)
		if not len(args) == len(func["params"]):
			raise ArgumentError(len(args), len(func["params"]), func["name"], self.file)
		if not len(args) == 0 and func["lang"] == "lamp":
			for i, arg in enumerate(args):
				self.vars[func["params"][i]] = arg
		if func["lang"] == "lamp":
			result = self.visit(func["block"])
		elif func["lang"] == "python":
			spec = importlib.util.spec_from_file_location(str(Path(func["module"]).stem), func["module"])
			extern = importlib.util.module_from_spec(spec)
			sys.modules[str(Path(func["module"]).stem)] = extern
			spec.loader.exec_module(extern)
			func_python = getattr(extern.LampExtern(), func["name"])
			result = func_python(*args)
		if type(result).__name__ == "list":
			for i in flatten(result):
				return i
		elif not result == None:
			return result
		if not len(args) == 0 and func["lang"] == "lamp":
			for i, arg in enumerate(args):
				self.vars.pop(func["params"][i])

	def import_stmt(self, tree):
		"""Import functions from source files
		
		import hello.lmp
		"""
		from pathlib import Path

		module_name = tree.children[0].value
		try:
			tree.children[1]
			load_pkg = False
		except IndexError:
			load_pkg = True
		if load_pkg:
			try:
				tree.children[1].children[0]
				has_list = True
			except IndexError:
				has_list = False
			if has_list:
				imp_list = []
				for name in tree.children[1].children:
					imp_list.append(name.value)
				with open(Path(getcwd(), module_name[1:] + ".lmp"), "r") as f:
					# TODO: Fix module imports
					# Supposed to be called but never is
					import_lex = Lark(grammar, parser="lalr")
					import_parser = CalculateTree()
					text = f.read()
					ast = import_lex.parse(text)
					import_parser.visit(ast)
					gen_funcs = import_parser.funcs
					filter_list = [
						func for func in gen_funcs if func["name"] == imp_list["name"]
					]
					new_funcs = self.funcs + filter_list
					self.funcs = new_funcs
		else:
			try:
				tree.children[1].children[0]
				has_list = True
			except IndexError:
				has_list = False
			if has_list:
				imp_list = []
				for name in tree.children[1].children:
					imp_list.append(name.value)
				module_file = Path(getcwd(), module_name[1:] + ".lmp")
				with module_file.open("r") as f:
					# Called when a filtered import (has a import list)
					# Ex: import test.lmp (test)
					import_lex = Lark(grammar, parser="lalr")
					import_parser = CalculateTree(module_name[1:])
					text = f.read()
					ast = import_lex.parse(text)
					import_parser.visit(ast)
					gen_funcs = import_parser.funcs
					filter_list = []
					for func in gen_funcs:
						if func["namespace"] == module_name[1:]:
							if func["name"] in imp_list:
								filter_list.append(func)
						else:
							filter_list.append(func)
					print(gen_funcs)
					print(filter_list)
					new_funcs = self.funcs + filter_list
					self.funcs = new_funcs
			else:
				is_pkg = False
				if module_name[1:].count(":") == 1:
					module_id = module_name[1:].split(":")
					if module_id[0] == "pkg": 
						is_pkg = True
						module_file = Path(getcwd(), "candlepkgs", module_name[1:].split(":")[1] + ".lmp")
					else:
						raise InvalidPackageProvider(module_id[0], self.file)
				elif module_name[1:].count(":") == 0:
					module_file = Path(getcwd(), module_name[1:] + ".lmp")         
				with module_file.open("r") as f:
					# Called when a common import (does not have a import list)
					# Ex: import test.lmp
					import_lex = Lark(grammar, parser="lalr")
					if is_pkg:
						import_parser = CalculateTree(module_name[1:].split(":")[1])
					else:
						import_parser = CalculateTree(module_name[1:])
					text = f.read()
					ast = import_lex.parse(text)
					import_parser.visit(ast)
					import_funcs = []
					for func in import_parser.funcs:
						if is_pkg:
							func["module"] = module_name[1:].split(":")[1]
						else:
							func["module"] = module_name[1:]
						import_funcs.append(func)
					new_funcs = self.funcs + import_funcs
					self.funcs = new_funcs
					
	def meta_function(self, tree):
		"""Meta function
		
		Ex. `@extern("python", hello.py)
		hello()`
		"""
		from pathlib import Path
		from inspect import signature
		keyword = tree.children[0].value
		args = self.visit(tree.children[1])
		if keyword == "extern":
			if args[0] == "python":
				spec = importlib.util.spec_from_file_location(str(Path(getcwd(), args[1]).stem), str(Path(getcwd(), args[1])))
				extern = importlib.util.module_from_spec(spec)
				sys.modules[Path(getcwd(), args[1]).stem] = extern
				spec.loader.exec_module(extern)
				func = getattr(extern.LampExtern(), args[2])
				sig = signature(func)
				params = list(sig.parameters.keys())
				func_dict = {"name": args[2], "params": params, "block": None, "namespace": self.file, "module": str(Path(getcwd(), args[1])), "lang": "python"}
				self.funcs.append(func_dict)

	def struct(self, tree):
		name = tree.children[0].value
		members = []
		for member in tree.children[1].children:
			members.append(member.value)
		self.structs.append({"name": name, "members": members, "namespace": self.file}) 

	def struct_ref(self, tree):
		namespace = tree.children[0].value
		name = tree.children[1].value
		for struct in self.structs:
			if struct["namespace"] == namespace and struct["name"] == name:
				return struct
	
	def struct_val(self, tree):
		var = tree.children[0].value
		value = tree.children[1].value
		try:
			return self.vars[var]["values"][value]
		except KeyError:
			raise InvalidProperty(value, f"{self.vars[var]["namespace"]}:{self.vars[var]["name"]}", self.file)
	
	def assign_struct(self, tree):
		var = tree.children[0].value
		val = tree.children[1].value
		output = self.visit(tree.children[2])
		struct = self.vars[var]
		if val not in struct["members"]:
			raise InvalidProperty(val, f"{struct["namespace"]}:{struct["name"]}", self.file)
		struct["values"][val] = output
		self.vars[var] = struct

# Command definition
@app.command()
def main(
	file: Annotated[Optional[str], typer.Argument()] = "REPL",
	repl: Annotated[
		str, typer.Option("--repl", "-r", help="Pass a MathLamp expression to the repl")
	] = "",
	error_hook: Annotated[
		bool,
		typer.Option(
			"--error",
			"-e",
			help="Use default Python error hook and disable MathLamp errors",
		),
	] = False
):
	from pathlib import Path

	if error_hook:
		sys.excepthook = sys.__excepthook__
	else:
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
			print(calc.funcs)
			if not val == None:
				print(val)
	else:
		try:
			with open(str(Path(getcwd(), file)), "r") as f:
				code = f.read()
				tree = calc_parser.parse(code)
				CalculateTree(Path(file).stem).visit(tree)

		except FileNotFoundError as e:
			if not error_hook:
				raise MissingFile(file)
			else:
				raise e


if __name__ == "__main__":
	app()
