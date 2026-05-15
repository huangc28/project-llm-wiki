#!/bin/sh
set -eu

repo_url="https://github.com/huangc28/project-llm-wiki.git"
install_dir="${PROJECT_LLM_WIKI_HOME:-$HOME/.local/share/project-llm-wiki}"

if [ ! -d "$install_dir" ]; then
  mkdir -p "$(dirname "$install_dir")"
  git clone "$repo_url" "$install_dir"
elif [ -d "$install_dir/.git" ]; then
  git -C "$install_dir" pull --ff-only
else
  echo "Install directory exists but is not a git checkout: $install_dir" >&2
  echo "Set PROJECT_LLM_WIKI_HOME to another path or move that directory first." >&2
  exit 2
fi

python3 "$install_dir/skills/project-llm-wiki/scripts/project_wiki.py" install "$@"
echo 'Restart Codex, then run $project-wiki-init inside a target Git repo.'
