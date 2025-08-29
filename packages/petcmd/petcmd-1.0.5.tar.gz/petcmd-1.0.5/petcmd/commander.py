
import sys
import traceback
from typing import Callable, Optional, Iterable

from petcmd.argparser import ArgParser
from petcmd.command import Command
from petcmd.exceptions import CommandException
from petcmd.interface import Interface
from petcmd.utils import (validate_type_hints, shell_complete_t, parse_docs,
	setup_shell_completion, remove_shell_completion, setup_zshrc_for_completion)

class Commander:

	def __init__(self, error_handler: Callable[[Exception], None] = None,
			compact_commands_list: bool = False,
			autocomplete_description: bool = True):
		self.error_handler = error_handler
		self.compact_commands_list = compact_commands_list
		self.autocomplete_description = autocomplete_description
		self.__commands: list[Command] = []
		self.__completion_commands = [
			"setup-shell-completion",
			"remove-shell-completion",
			"setup-zshrc",
		]

		@self.command("help", shell_complete={"command": lambda: sum([c.cmds for c in self.__commands], ())})
		def help_command(command: str = None):
			"""
			Show a help message or usage message when a command is specified.

			:param command: Command for which instructions for use will be displayed.
			"""
			self.__help_command(command)

		@self.command("help-completion")
		def help_completion():
			"""Show a help message for completion commands."""
			Interface.commands_list([c for c in self.__commands if c.cmds[0] in self.__completion_commands])

		@self.command("setup-shell-completion")
		def __setup_shell_completion(alias: str = None):
			"""
			Set up a shell completion script for the current cli tool.
			Save it to ~/.zsh/completions/_alias.

			:param alias:   Alias for the cli tool completion.
							If not specified, the name of the current script is used.
			"""
			setup_shell_completion(alias)

		@self.command("remove-shell-completion")
		def __remove_shell_completion(alias: str = None):
			"""
			Remove a shell completion script for the current cli tool.
			Search it in ~/.zsh/completions/_alias.

			:param alias:   Alias for the cli tool completion.
							If not specified, the name of the current script is used.
			"""
			remove_shell_completion(alias)

		@self.command("setup-zshrc")
		def __setup_zshrc_for_completion():
			"""Fill ~/.zshrc with commands to enable shell completion for zsh with ~/.zsh/completions/* files."""
			setup_zshrc_for_completion()

		self.__internal_commands = len(self.__commands)

	def command(self, *cmds: str, shell_complete: shell_complete_t = None):
		def dec(func: Callable) -> Callable:
			self.add_command(cmds, func, shell_complete)
			return func
		return dec

	def add_command(self, cmds: str | Iterable[str], func: Callable, shell_complete: shell_complete_t = None):
		cmds = (cmds,) if isinstance(cmds, str) else cmds
		if not cmds:
			cmds = (func.__name__.replace("_", "-"),)
		shell_complete = shell_complete if isinstance(shell_complete, dict) else {}
		for command in self.__commands:
			if command.match(cmds):
				raise CommandException(f"Duplicated command: {", ".join(cmds)}")
		validate_type_hints(func, shell_complete)
		self.__commands.append(Command(cmds, func, shell_complete))

	def process(self, argv: list[str] = None):
		if argv is None:
			argv = sys.argv[1:]

		if len(argv) > 0 and argv[0] == "--shell-completion":
			try:
				if len(argv) == 3:
					self.__print_commands()
				elif command := self.__find_command(argv[2]):
					ArgParser(argv[3:], command).autocomplete(int(argv[1]) - 1, self.autocomplete_description)
			except Exception: pass
			return

		command = self.__find_command(argv[0] if len(argv) > 0 else "help")
		if command is None:
			print(f"\nUnknown command '{argv[0]}'")
			self.__help_command()
			return

		try:
			args, kwargs = ArgParser(argv[1:], command).parse()
			command.func(*args, **kwargs)
		except CommandException as e:
			print("\n" + str(e))
			Interface.command_usage(command)
		except Exception as e:
			if isinstance(self.error_handler, Callable):
				self.error_handler(e)
			else:
				print("\n" + traceback.format_exc())

	def __find_command(self, cmd: str) -> Optional[Command]:
		for command in self.__commands:
			if command.match(cmd):
				return command

	def __print_commands(self):
		spaces = " "
		commands = self.__commands[self.__internal_commands:] + self.__commands[:self.__internal_commands]
		docs = {}
		if self.autocomplete_description:
			for command in commands:
				docs[command] = " ".join(parse_docs(command.func)[0])
		show_docs = any(doc for doc in docs.values())
		for command in commands:
			if command.cmds[0] in self.__completion_commands:
				continue
			if show_docs and not docs[command]:
				docs[command] = spaces
				spaces += " "
			for synonym in command.cmds:
				print(f"{synonym}\t{docs[command]}" if show_docs else synonym)

	def __help_command(self, cmd: str = None):
		if cmd and (command := self.__find_command(cmd)):
			Interface.command_usage(command)
			return
		commands = self.__commands[self.__internal_commands:] + self.__commands[:self.__internal_commands]
		Interface.commands_list([c for c in commands if c.cmds[0] not in self.__completion_commands],
			self.compact_commands_list)
