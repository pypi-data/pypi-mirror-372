
ZSH_AUTOCOMPLETE_TEMPLATE = """
#compdef {alias}

local curcontext="$curcontext" state line
local -a completions options described
local all_described=1

# current-2 because indexes start from 1 and need to remove tool name from start
completions=("${{(@f)$({alias} --shell-completion "$((CURRENT-2))" "${{words[@]:1}}")}}")
completions=(${{completions:#}})
(( $#completions )) || return 1

if [[ "${{completions[1]}}" == "__files__" ]]; then
  _files
  return 0
fi

local opt desc
for line in "${{completions[@]}}"; do
  opt="${{line%%$'\\t'*}}"
  desc="${{line#*$'\\t'}}"
  if [[ "$opt" == "$desc" ]]; then
    desc=""
    all_described=0
  fi
  options+=("$opt")
  described+=("$opt:$desc")
done

options=(${{options:#}})

if (( all_described )); then
  described=(${{described:#}})
  _describe 'options' described -o nosort -V petcmd
  return 0
elif (( ${{#options[@]}} )); then
  compadd -o nosort -V petcmd -a options
  return 0
fi

return 1
""".lstrip()
