---
quick_id: 260513-q3w
status: complete
description: Expose project-wiki mode aliases as Codex dollar-trigger skills
completed: 2026-05-13
commit: 849d58d
---

# Quick Task 260513-q3w Summary

## Result

Exposed `project-wiki-init`, `project-wiki-lint`, `project-wiki-query`, and `project-wiki-ingest` as real thin Codex skill aliases.

## Changes

- Added four repo-tracked alias skill folders under `skills/`.
- Updated `command-surface.md` to document implemented `$project-wiki-*` aliases.
- Added package tests that assert alias skill metadata exists and routes back to `project-llm-wiki`.
- Created user-scope symlinks in `~/.codex/skills` for all four aliases.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests -p "test_project_wiki_package.py"` - 16 tests passed.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests` - 128 tests passed.
- `git diff --check` - passed.
- `~/.codex/skills/project-wiki-init`, `project-wiki-lint`, `project-wiki-query`, and `project-wiki-ingest` symlinks resolve to the repo skill folders.

## Notes

Codex skill autocomplete may require a new or reloaded session before the new `$project-wiki-*` skill names appear.
