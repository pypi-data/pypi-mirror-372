
import os
import re
import sys
from pathlib import Path
from types import GenericAlias
from typing import Type, Optional, Any

from petcmd.command import Command
from petcmd.exceptions import CommandException
from petcmd.utils import PipeOutput, FilePath, get_signature, parse_docs

DEBUG = False
BOOLEAN_VALUES = ("0", "false", "1", "true")

def log(*args: Any):
	if not DEBUG: return
	with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "log.txt"), "a") as f:
		f.write(" ".join(map(str, args)) + "\n")

class ArgParser:

	def __init__(self, argv: list[str], command: Command = None):
		self.argv = argv
		self.command = command

		self.positionals, self.keyword, self.defaults, self.spec = get_signature(command.func)

		self.pipe_argument_name = self.__get_pipe_argument_name()
		self.pipe_argument_index = -1
		if self.pipe_argument_name in self.positionals:
			self.pipe_argument_index = self.positionals.index(self.pipe_argument_name)
			self.positionals.remove(self.pipe_argument_name)
		elif self.pipe_argument_name in self.keyword:
			self.keyword.remove(self.pipe_argument_name)

		# values specified by keywords
		self.values: dict[str, Optional[str | list[str] | dict[str, str]]] = {}
		# list of positional values
		self.free_values: list[str] = []
		self.autocomplete_values = []

	def parse(self) -> tuple[list, dict]:

		self.__parse_argv()

		# number of positional arguments specified by keywords
		args_as_keyword = len([arg for arg in self.positionals if arg in self.values])
		# check all positional arguments are present
		if len(self.free_values) + args_as_keyword < len(self.positionals):
			# the number of the free values and positional arguments specified by keywords
			# less than the number of required positional arguments
			raise CommandException("Invalid usage: missing required positional arguments")

		# checking positional arguments doesn't follow keyword arguments
		for i, arg in enumerate(self.positionals):
			if arg in self.values:
				for j, arg_ in enumerate(self.positionals[i + 1:]):
					if arg_ not in self.values:
						raise CommandException(f"Invalid usage: positional argument '{arg_}' "
												f"follows keyword argument '{arg}'")
				break

		# checking unnecessary positional arguments
		if self.spec.varargs is None:
			if args_as_keyword > 0 and len(self.free_values) != len(self.positionals) - args_as_keyword:
				# varargs is None and some positional arguments were specified by keyword,
				# so it's denied to specify keyword arguments by position
				raise CommandException("Invalid usage: unexpected number of positional arguments")
			if args_as_keyword == 0 and len(self.free_values) > len(self.positionals) + len(self.keyword):
				# varargs is None and the number of all arguments is lower than the number of given free values
				raise CommandException("Invalid usage: unexpected number of positional arguments")

		# checking unnecessary keyword arguments
		unexpected_keyword = [arg for arg in self.values if arg not in self.positionals and arg not in self.keyword]
		if self.spec.varkw is None and len(unexpected_keyword) > 0:
			raise CommandException("Invalid usage: unexpected number of keyword arguments "
				+ f"({", ".join(unexpected_keyword)})")

		# number of positional arguments specified by position
		args_as_positional = len(self.positionals) - args_as_keyword
		# map of positional arguments names to values specified by position
		args: dict = dict(zip(self.positionals[:args_as_positional], self.free_values[:args_as_positional]))
		# extend args with positional arguments specified by keywords
		args.update({arg: self.values[arg] for arg in self.positionals[args_as_positional:]})
		# the rest of values specified by position after positional arguments were taken
		extra_args = self.free_values[args_as_positional:]

		# the number of keyword arguments specified by position
		# if varargs presents in the function signature specifying keyword argument by position is denied
		kwargs_as_positional = len(extra_args) if self.spec.varargs is None else 0
		# checking if a keyword duplicated any keyword argument specified by position
		for arg in self.keyword[:kwargs_as_positional]:
			if arg in self.values:
				raise CommandException(f"Invalid usage: keyword argument {arg} "
										f"have been specified as positional already")

		# map of keyword arguments names to values specified by corresponding keywords
		keyword_values = {arg: value for arg, value in self.values.items() if arg not in self.positionals}
		keyword_values.update(dict(zip(self.keyword[:kwargs_as_positional], extra_args)))
		if kwargs_as_positional:
			extra_args.clear()

		for arg in args.keys():
			args[arg] = self.__parse_value(args[arg], self.spec.annotations.get(arg))
		for kwarg in keyword_values:
			keyword_values[kwarg] = self.__parse_value(keyword_values[kwarg], self.spec.annotations.get(kwarg))
		extra_args = [self.__parse_value(value, self.spec.annotations.get(self.spec.varargs)) for value in extra_args]
		positional_values = [*args.values(), *extra_args]

		if self.pipe_argument_name is not None:
			if not sys.stdin.isatty():
				pipe = sys.stdin.read().strip() or self.defaults.get(self.pipe_argument_name, "")
			else:
				pipe = ""
			if self.pipe_argument_index != -1:
				positional_values.insert(self.pipe_argument_index, pipe)
			else:
				keyword_values[self.pipe_argument_name] = pipe

		return positional_values, keyword_values

	def autocomplete(self, index: int, descriptions_enabled: bool = True):

		log("\nautocomplete", index, self.argv)

		pointer = self.__parse_argv(end=index, skip_errors=True)
		free_values_before_index = len(self.free_values)
		self.__parse_argv(start=index + 1, end=len(self.argv), skip_errors=True)

		param = self.__find_last_param(pointer - 1)
		argument, typehint, generics = self.__param_info(param)

		# app command --data *something*
		# the latest item before the current is param
		if param and param == self.__match_param(self.argv[pointer - 1]):
			log("check param", param)
			if not argument and self.spec.varkw:
				argument = self.spec.varkw
				typehint = self.__get_typehint_origin(argument)
			if complete := self.command.get_shell_complete(argument):
				self.__print_autocomplete_values(complete)
			elif typehint == bool or generics and generics[0] == bool:
				self.__print_bool_autocomplete()
			elif typehint in (FilePath, Path) or generics and generics[0] in (FilePath, Path):
				self.__print_files_autocomplete()
			if typehint not in (list, tuple, set, dict):
				if typehint != bool or self.__boolean_require_value(argument):
					return

		# app command --list 1 2 3 4 *something*
		# all values between the latest param and the current are iterables
		elif param and typehint in (list, tuple, set, dict):
			log("check iterable", param)
			if complete := self.command.get_shell_complete(argument):
				self.__print_autocomplete_values(complete)
			elif typehint in (list, set) or typehint == tuple and len(generics) == 1:
				if generics and generics[0] == bool:
					self.__print_bool_autocomplete()
				elif generics and generics[0] in (FilePath, Path):
					self.__print_files_autocomplete()
					return
			elif typehint == tuple and len(self.values.get(argument, [])) < len(generics):
				generic = generics[len(self.values[argument])]
				if generic == bool:
					self.__print_bool_autocomplete()
				elif generic in (FilePath, Path):
					self.__print_files_autocomplete()
				return

		# app command value --data value *something*
		# there are required positionals to specify
		elif (free_values_before_index < len(self.positionals)
				and self.positionals[free_values_before_index] not in self.values):
			log("check next positional argument", self.positionals[free_values_before_index])
			argument = self.positionals[free_values_before_index]
			typehint = self.__get_typehint_origin(argument)
			if complete := self.command.get_shell_complete(argument):
				self.__print_autocomplete_values(complete)
			elif typehint == bool:
				self.__print_bool_autocomplete()
			elif typehint in (FilePath, Path):
				self.__print_files_autocomplete()
				return

		# app command value --data value *something*
		# all positionals were specified and there are extra *args
		elif self.spec.varargs:
			log("check extra *args")
			typehint = self.__get_typehint_origin(self.spec.varargs)
			if complete := self.command.get_shell_complete(self.spec.varargs):
				self.__print_autocomplete_values(complete)
			elif typehint == bool:
				self.__print_bool_autocomplete()
			elif typehint in (FilePath, Path):
				self.__print_files_autocomplete()
				return

		log("print params")
		args_as_positional = len([arg for arg in self.positionals if arg not in self.values])
		extra_args = self.free_values[args_as_positional:free_values_before_index]
		kwargs_as_positional = len(extra_args) if self.spec.varargs is None else 0
		docs = parse_docs(self.command.func)[1] if descriptions_enabled else {}
		args = {}
		for arg in [*self.positionals[free_values_before_index:], *self.keyword[kwargs_as_positional:]]:
			if arg not in self.values:
				args[arg] = " ".join(docs.get(arg, []))
		show_docs = any(doc for doc in args.values())
		spaces = " "
		for arg, doc in args.items():
			if show_docs and not doc:
				doc = spaces
				spaces += " "
			for alias in self.command.get_aliases(arg):
				option = "-" * (1 if len(alias) == 1 else 2) + alias
				print(f"{option}\t{doc}" if show_docs else option)

	def __parse_argv(self, start: int = 0, end: int = -1, skip_errors: bool = False) -> int:
		pointer = start
		end = len(self.argv) if end == -1 else end
		while pointer < end:
			param = self.__match_param(self.argv[pointer])

			if not param:
				self.free_values.append(self.argv[pointer])
				pointer += 1
				continue

			argument = self.command.get_argument(param, param)
			if not skip_errors and argument in self.values:
				raise CommandException(f"Invalid usage: duplicate argument {argument}")
			typehint = self.__get_typehint_origin(argument)
			is_last = pointer == end - 1
			next_param = self.__find_next_param_index(pointer + 1, end)
			next_value_is_boolean = not is_last and self.argv[pointer + 1].lower() in BOOLEAN_VALUES

			if (typehint == bool
					and argument not in self.positionals
					and self.defaults.get(argument) is False
					and not next_value_is_boolean):
				self.values[argument] = "True"
				pointer += 1
				continue
			elif is_last or pointer + 1 == next_param:
				if not skip_errors:
					raise CommandException(f"Invalid usage: missing {param} param value")
				self.values[argument] = None
				pointer += 1
			elif typehint in (list, tuple, set):
				self.values[argument] = self.argv[pointer + 1:next_param]
				pointer = next_param
			elif typehint == dict:
				self.values[argument] = dict(value.split("=", 1) for value in self.argv[pointer + 1:next_param])
				pointer = next_param
			else:
				self.values[argument] = self.argv[pointer + 1]
				pointer += 2
		return pointer

	def __find_last_param(self, pointer: int, start: int = 0) -> Optional[str]:
		param = None
		while pointer >= start and not (param := self.__match_param(self.argv[pointer])):
			pointer -= 1
		return param

	def __find_next_param_index(self, pointer: int, end: int = -1) -> int:
		end = len(self.argv) if end == -1 else end
		while pointer < end and not self.__match_param(self.argv[pointer]):
			pointer += 1
		return pointer

	def __get_pipe_argument_name(self) -> Optional[str]:
		for arg, typehint in self.spec.annotations.items():
			if typehint == PipeOutput:
				return arg

	def __param_info(self, param: Optional[str]):
		if not param or not (argument := self.command.get_argument(param)):
			return None, None, None
		typehint = self.spec.annotations.get(argument)
		if isinstance(typehint, GenericAlias):
			return argument, typehint.__origin__, typehint.__args__
		return argument, typehint, []

	def __get_typehint_origin(self, argument: str):
		typehint = self.spec.annotations.get(argument)
		if isinstance(typehint, GenericAlias):
			return typehint.__origin__
		return typehint

	def __boolean_require_value(self, argument: str) -> bool:
		if argument not in self.positionals:
			return self.defaults.get(argument) is not False
		return True

	@classmethod
	def __parse_value[T](cls, value: str, typehint: Type[T]) -> T:
		origin = typehint.__origin__ if isinstance(typehint, GenericAlias) else typehint
		generics = list(typehint.__args__) if isinstance(typehint, GenericAlias) else []

		if origin in (str, FilePath, None):
			return value
		if origin == Path:
			return Path(value)
		elif origin in (int, float):
			try:
				return typehint(value)
			except ValueError:
				raise CommandException(f"{value} can't be converted to {typehint}")
		elif origin == bool:
			if value.lower() in ("1", "true"):
				return True
			elif value.lower() in ("0", "false"):
				return False
			raise CommandException(f"{value} can't be converted to {typehint}")
		elif isinstance(value, list):
			if origin in (list, set):
				if generics:
					return origin(cls.__parse_value(item, generics[0]) for item in value)
				return origin(value)
			if origin == tuple:
				if not generics:
					return origin(value)
				elif len(generics) == 1:
					return origin(cls.__parse_value(item, generics[0]) for item in value)
				elif len(generics) != len(value):
					raise CommandException("Mismatch between the number of elements and tuple generic types")
				return origin(cls.__parse_value(value[i], generics[i]) for i in range(len(value)))
		elif isinstance(value, dict):
			if not generics:
				return value
			if len(generics) != 2:
				raise CommandException("Invalid number of dict generic types, should be 2")
			key_type, value_type = generics
			return {cls.__parse_value(k, key_type): cls.__parse_value(v, value_type) for k, v in value.items()}
		elif origin in (list, tuple, set, dict):
			try:
				obj = eval(value)
				if isinstance(obj, origin):
					return obj
			except Exception:
				pass
			raise CommandException(f"{value} can't be converted to {typehint}")
		raise CommandException(f"{value} can't be converted to {typehint}")

	@staticmethod
	def __match_param(string: str) -> Optional[str]:
		if match := re.match("^(-[a-zA-Z]|--[a-zA-Z_][a-zA-Z0-9_-]*)$", string):
			return match.group(1).lstrip("-")

	@staticmethod
	def __print_bool_autocomplete():
		log("print bool values")
		for item in BOOLEAN_VALUES:
			print(item)

	@staticmethod
	def __print_files_autocomplete():
		log("print __files__")
		print("__files__")

	@staticmethod
	def __print_autocomplete_values(values):
		log("print values", values)
		for value in values:
			print(value)
