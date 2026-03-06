import sys

import rich
from lark.exceptions import UnexpectedToken

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