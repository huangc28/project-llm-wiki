#!/bin/sh
set -eu

repo_url="https://github.com/huangc28/project-llm-wiki.git"
tmp_dir=""

cleanup() {
  if [ -n "$tmp_dir" ] && [ -d "$tmp_dir" ]; then
    rm -rf "$tmp_dir"
  fi
}
trap cleanup EXIT INT TERM

if [ -n "${PROJECT_LLM_WIKI_HOME:-}" ]; then
  install_dir="$PROJECT_LLM_WIKI_HOME"
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
else
  tmp_dir="$(mktemp -d)"
  install_dir="$tmp_dir/project-llm-wiki"
  git clone "$repo_url" "$install_dir"
fi

python3 "$install_dir/skills/project-llm-wiki/scripts/project_wiki.py" install "$@"
echo 'Restart Codex, then run $project-wiki-init inside a target Git repo.'
