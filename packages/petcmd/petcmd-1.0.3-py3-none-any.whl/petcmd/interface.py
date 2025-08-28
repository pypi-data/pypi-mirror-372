
from petcmd.command import Command
from petcmd.utils import get_signature, detect_program_name, parse_docs

program_name = detect_program_name()

class Interface:

	@classmethod
	def commands_list(cls, commands: list[Command], compact_commands_list: bool = False):

		def docs_view(c: Command) -> str:
			if docs := parse_docs(c.func)[0]:
				return f"\n{" " * 8}" + f"\n{" " * 8}".join(docs)
			return ""

		def compact_view(c: Command):
			return f"{" " * 4}{", ".join(c.cmds)}{docs_view(c)}"

		def full_view(c: Command):

			positionals, keyword, defaults, spec = get_signature(c.func)

			def positionals_view() -> str:
				if not positionals:
					return ""
				return " ".join(positionals) + " "

			def keywords_list_view() -> str:
				return " ".join(f"[-{arg}]" for arg in keyword)

			return f"{" " * 4}{"|".join(c.cmds)} {positionals_view()}{keywords_list_view()}{docs_view(c)}"

		view = compact_view if compact_commands_list else full_view
		print(f"\n{program_name} commands list:\n\n" + "\n\n".join(map(view, commands)) + "\n")

	@classmethod
	def command_usage(cls, command: Command):
		positionals, keyword, defaults, spec = get_signature(command.func)
		docs, args_docs = parse_docs(command.func)

		def command_name_view() -> str:
			if command.cmds[0] == "__main__":
				return program_name
			return f"{program_name} {command.cmds[0]}"

		def positionals_view() -> str:
			if not positionals:
				return ""
			return " ".join(positionals) + " "

		def keywords_list_view() -> str:
			return " ".join(f"[-{arg}]" for arg in keyword)

		def positional_description_view(arg: str) -> str:
			return f"{arg:<{longest_pos_name + 1}}{typehint_view(arg):<{longest_pos_hint + 1}}" \
				+ f"\n{" " * (longest_pos_name + longest_pos_hint + 2)}".join(args_docs.get(arg, []))

		def typehint_view(arg: str) -> str:
			hint = spec.annotations.get(arg)
			if not hint:
				return ""
			if isinstance(hint, type):
				return hint.__name__
			return str(hint)

		def keyword_description_view(arg: str) -> str:
			desc = f"{aliases_view(arg):<{longest_kw_name + 1}}"
			desc += f"{typehint_view(arg):<{longest_kw_hint + 1}}"
			desc += default_value_view(arg)
			if arg in args_docs:
				desc += "\n" + " " * 16 + f"\n{" " * 16}".join(args_docs[arg])
			return " " * 8 + desc

		def aliases_view(arg: str) -> str:
			return " ".join(alias_view(alias) for alias in command.get_aliases(arg))

		def alias_view(alias: str):
			if len(alias) == 1:
				return f"-{alias}"
			return f"--{alias}"

		def default_value_view(arg: str):
			if arg not in defaults:
				return ""
			return f"[default: {defaults[arg]}]"

		desc = f"Usage: {command_name_view()} {positionals_view()}{keywords_list_view()}"
		if docs:
			desc += f"\n\n{" " * 8}{"\n\t".join(docs)}"
		if positionals:
			longest_pos_name = max(len(arg) for arg in positionals)
			if longest_pos_name < 7:
				longest_pos_name = 7
			longest_pos_hint = max(len(typehint_view(arg)) for arg in positionals)
			if longest_pos_hint < 7:
				longest_pos_hint = 7
			desc += "\n\n" + "\n".join(map(positional_description_view, positionals))
		if keyword:
			longest_kw_name = max(len(aliases_view(arg)) for arg in keyword)
			if longest_kw_name < 15:
				longest_kw_name = 15
			longest_kw_hint = max(len(typehint_view(arg)) for arg in keyword)
			if longest_kw_hint < 7:
				longest_kw_hint = 7
			desc += "\n\nOptions:\n" + "\n".join(map(keyword_description_view, keyword))

		print("\n" + desc + "\n")
