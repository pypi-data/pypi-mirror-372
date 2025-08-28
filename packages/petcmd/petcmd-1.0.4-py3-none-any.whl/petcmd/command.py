
import re
from typing import Callable, Iterable, Optional

from petcmd.utils import get_signature, shell_complete_t

class Command:

	def __init__(self, cmds: str | tuple[str, ...], func: Callable,
			shell_complete: shell_complete_t = None):
		self.cmds = (cmds,) if isinstance(cmds, str) else cmds
		self.func = func
		self.__shell_complete = shell_complete if shell_complete is not None else {}
		if not isinstance(self.__shell_complete, dict):
			raise TypeError("shell_complete must be a dict")

		self.__alias_to_argument = {}
		self.__argument_to_aliases = {}
		positionals, keyword, *_ = get_signature(self.func)
		for arg in [*positionals, *keyword]:
			self.__alias_to_argument[arg] = arg
			self.__alias_to_argument[arg.replace('_', '-')] = arg
			self.__argument_to_aliases[arg] = [arg.replace('_', '-')]
			first_letter = re.search(r"[a-zA-Z]", arg).group(0)
			if first_letter.lower() not in self.__alias_to_argument:
				self.__alias_to_argument[first_letter.lower()] = arg
				self.__argument_to_aliases[arg].append(first_letter.lower())
			elif first_letter.upper() not in self.__alias_to_argument:
				self.__alias_to_argument[first_letter.upper()] = arg
				self.__argument_to_aliases[arg].append(first_letter.upper())

	def match(self, cmd: str | tuple[str, ...]) -> bool:
		if isinstance(cmd, str):
			return cmd in self.cmds
		return any(c in cmd for c in self.cmds)

	def get_shell_complete(self, argument: str) -> Optional[Iterable]:
		complete = self.__shell_complete.get(argument)
		if isinstance(complete, Callable):
			complete = complete()
		if isinstance(complete, str):
			return (complete,)
		elif isinstance(complete, Iterable):
			return complete
		else:
			return None

	def get_aliases(self, argument: str) -> list[str]:
		return self.__argument_to_aliases.get(argument, [])

	def get_argument[T](self, alias: str, default: T = None) -> Optional[str | T]:
		return self.__alias_to_argument.get(alias, default)
