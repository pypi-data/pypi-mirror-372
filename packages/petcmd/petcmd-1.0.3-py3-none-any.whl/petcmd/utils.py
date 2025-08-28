
import os
import re
import sys
import inspect
from pathlib import Path
from types import GenericAlias
from typing import Callable, Iterable, Optional

from petcmd.autocompletion.zsh import ZSH_AUTOCOMPLETE_TEMPLATE
from petcmd.exceptions import CommandException

type shell_complete_t = dict[str, Iterable | Callable[[], Iterable | str] | str]

class PipeOutput(str):
	pass

class FilePath(str):
	pass

allowed_type_hints = (str, int, float, bool, list, tuple, set, dict, PipeOutput, FilePath, Path)

def get_signature(func: Callable):
	"""Returns positionals, keyword, defaults, spec"""
	spec = inspect.getfullargspec(func)
	positionals = spec.args if spec.defaults is None else spec.args[:-len(spec.defaults)]
	keyword = spec.kwonlyargs
	if spec.defaults is not None:
		keyword.extend(spec.args[-len(spec.defaults):])
	defaults = spec.kwonlydefaults or {}
	if spec.defaults is not None:
		defaults.update(dict(zip(spec.args[-len(spec.defaults):], spec.defaults)))
	return positionals, keyword, defaults, spec

def validate_type_hints(func: Callable, shell_complete: shell_complete_t = None):
	shell_complete = shell_complete if shell_complete is not None else {}
	pipe_argument = None
	spec = inspect.getfullargspec(func)
	for arg, typehint in spec.annotations.items():
		origin = typehint.__origin__ if isinstance(typehint, GenericAlias) else typehint
		generics = typehint.__args__ if isinstance(typehint, GenericAlias) else []
		if origin not in allowed_type_hints:
			raise CommandException("Unsupported typehint: petcmd supports only basic types: "
				+ ", ".join(map(lambda t: t.__name__, allowed_type_hints)))
		if any(generic not in allowed_type_hints for generic in generics):
			raise CommandException("Unsupported typehint generic: petcmd supports only basic generics: "
				+ ", ".join(map(lambda t: t.__name__, allowed_type_hints)))
		if arg in (spec.varargs, spec.varkw) and origin in (list, tuple, set, dict):
			raise CommandException("Unsupported typehint generic: petcmd doesn't support "
				+ "iterable typehints for *args and **kwargs")
		if origin == bool and shell_complete.get(arg):
			raise CommandException("Unsupported shell complete: bool typehint can't be used with shell completion")
		if origin in (list, set) and generics and generics[0] == bool and shell_complete.get(arg):
			raise CommandException("Unsupported shell complete: bool generic can't be used with shell completion")
		if typehint == PipeOutput and pipe_argument is not None:
			raise CommandException("Invalid typehints: you can't specify more than one PipeOutput argument")
		if typehint == PipeOutput and pipe_argument is None:
			pipe_argument = arg
	if pipe_argument is not None and pipe_argument in (spec.varargs, spec.varkw):
		raise CommandException("Invalid typehints: you can't specify PipeOutput argument as varargs or varkw")

def detect_program_name() -> str:
	_main = sys.modules.get("__main__")
	if _main is not None:
		path = getattr(_main, "__file__", "")
		if path:
			name = os.path.splitext(os.path.basename(path))[0]
			if name and name != "__main__":
				return name
		package = getattr(_main, "__package__", "")
		if package:
			return package.lstrip('.')

	path = sys.argv[0]
	if path and path not in ("-c", "-m"):
		name = os.path.splitext(os.path.basename(path))[0]
		if name and name != "__main__":
			return name

	return "cli"

def parse_docs(func: Callable) -> tuple[list[str], dict[str, list[str]]]:
	"""Returns a list of docs paragraphs and map of arguments to a list of argument docs paragraphs"""
	docs = func.__doc__
	if not docs:
		return [], {}
	docs = inspect.cleandoc(docs)
	desc = []
	roles = []

	lines = docs.splitlines()
	i = 0
	while i < len(lines):
		if match := re.match("^:([a-zA-Z]+) ?([^:]*): ?(.*)$", lines[i].strip()):
			role, arg, value = match.groups()
			indent = len(re.match(r"^(\s*)", lines[i]).group(0))
			content = [value.strip()]
			i += 1
			while i < len(lines) and len(re.match(r"^(\s*)", lines[i]).group(0)) > indent:
				content.append(lines[i].strip())
				i += 1
			roles.append({"name": role.strip(), "arg": arg.strip(), "content": content})
			continue
		elif not len(roles):
			desc.append(lines[i].strip())
		i += 1

	while desc and not desc[0]:
		desc.pop(0)
	while desc and not desc[-1]:
		desc.pop()

	return desc, {role["arg"]: role["content"] for role in roles if role["name"] == "param"}

def setup_shell_completion(alias: Optional[str] = None):
	if alias is None:
		alias = os.path.basename(sys.argv[0]).rsplit(".", 1)[0]
	completions = os.path.join(os.path.expanduser("~"), ".zsh", "completions")
	os.makedirs(completions, exist_ok=True)
	with open(os.path.join(completions, f"_{alias}"), "w") as f:
		f.write(ZSH_AUTOCOMPLETE_TEMPLATE.format(alias=alias))
	print(f"Shell completion script for {alias} has been saved to {completions}. Restart terminal to load it.")

def remove_shell_completion(alias: str):
	os.remove(os.path.join(os.path.expanduser("~"), ".zsh", "completions", f"_{alias}"))

def setup_zshrc_for_completion():
	home = os.path.expanduser("~")
	zshrc = os.path.join(home, ".zshrc")
	completions = os.path.join(home, ".zsh", "completions")
	if not os.path.exists(zshrc):
		with open(zshrc, "w") as f:
			f.write("")
	with open(zshrc, "r") as f:
		content = f.read()
	commands = [
		f"fpath=({completions} $fpath)",
		"autoload -Uz compinit && compinit",
	]
	with open(zshrc, "a") as f:
		if any(command not in content for command in commands):
			f.write("\n")
		for command in commands:
			if command not in content:
				f.write(f"{command}\n")
