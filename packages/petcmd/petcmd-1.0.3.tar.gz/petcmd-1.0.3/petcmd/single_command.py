import os
import sys
import traceback
from typing import Callable, Optional

from petcmd.argparser import ArgParser
from petcmd.command import Command
from petcmd.exceptions import CommandException
from petcmd.interface import Interface
from petcmd.utils import (validate_type_hints, shell_complete_t,
	setup_shell_completion, remove_shell_completion, setup_zshrc_for_completion, parse_docs)

class SingleCommand:

	def __init__(self, error_handler: Callable[[Exception], None] = None, autocomplete_description: bool = True,
			autocomplete_internal_commands: bool = False):
		self.error_handler = error_handler
		self.autocomplete_description = autocomplete_description
		self.autocomplete_internal_commands = autocomplete_internal_commands
		self.__command = None
		self.__internal_commands: list[tuple[tuple[str, ...], Callable[[list[str]], None], bool]] = []

		@self.__internal_command("--help", "-h")
		def help_message(*_):
			"""Show a usage message."""
			Interface.command_usage(self.__command)

		@self.__internal_command("--setup-shell-completion")
		def setup_shell_completion_(argv):
			"""Set up a shell completion script for the current cli tool. Save it to ~/.zsh/completions/_alias."""
			setup_shell_completion(os.path.basename(sys.argv[0]) if len(argv) == 1 else argv[1])

		@self.__internal_command("--remove-shell-completion")
		def remove_shell_completion_(argv):
			"""Remove a shell completion script for the current cli tool. Search it in ~/.zsh/completions/_alias."""
			remove_shell_completion(os.path.basename(sys.argv[0]) if len(argv) == 1 else argv[1])

		@self.__internal_command("--setup-zshrc-for-completion")
		def setup_zshrc_for_completion_(*_):
			"""Fill ~/.zshrc with commands to enable shell completion for zsh with ~/.zsh/completions/* files."""
			setup_zshrc_for_completion()

		@self.__internal_command("--shell-completion", autocomplete=False)
		def shell_completion_(argv):
			try: ArgParser(argv[2:], self.__command).autocomplete(int(argv[1]), self.autocomplete_description)
			except Exception: pass
			if self.autocomplete_internal_commands and int(argv[1]) == 0 and len(argv) == 3:
				for commands, func, autocomplete in self.__internal_commands:
					if autocomplete:
						print(commands[0], " ".join(parse_docs(func)[0]), sep="\t")

	def use(self, shell_complete: shell_complete_t = None):
		def dec(func: Callable) -> Callable:
			self.register_command(func, shell_complete)
			return func
		return dec

	def register_command(self, func: Callable, shell_complete: shell_complete_t = None):
		shell_complete = shell_complete if isinstance(shell_complete, dict) else {}
		if self.__command is not None:
			raise CommandException("You can't use more than one command with SingleCommand")
		validate_type_hints(func, shell_complete)
		self.__command = Command(("__main__",), func, shell_complete)

	def process(self, argv: list[str] = None):
		if argv is None:
			argv = sys.argv[1:]

		if len(argv) >= 1 and (func := self.__match_internal_command(argv[0])):
			func(argv)
			return

		try:
			args, kwargs = ArgParser(argv, self.__command).parse()
			self.__command.func(*args, **kwargs)
		except CommandException as e:
			print("\n" + str(e))
			Interface.command_usage(self.__command)
		except Exception as e:
			if isinstance(self.error_handler, Callable):
				self.error_handler(e)
			else:
				print("\n" + traceback.format_exc())

	def __internal_command(self, *commands: str, autocomplete: bool = True):
		def dec(func: Callable[[list[str]], None]) -> Callable[[list[str]], None]:
			self.__internal_commands.append((commands, func, autocomplete))
			return func
		return dec

	def __match_internal_command(self, command: str) -> Optional[Callable[[list[str]], None]]:
		for cmds, func, _ in self.__internal_commands:
			if command in cmds:
				return func
