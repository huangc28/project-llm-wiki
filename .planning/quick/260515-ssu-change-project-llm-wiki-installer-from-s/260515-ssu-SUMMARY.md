---
quick_id: 260515-ssu
slug: change-project-llm-wiki-installer-from-s
status: complete
date: 2026-05-15
commit: 1228801
---

# Quick Task 260515-ssu Summary

Changed Project LLM Wiki install from symlink-based setup to copied Codex skill directories with marker ownership.

## Result

- `install.sh` now clones to a temporary checkout by default and removes it on exit.
- `project-wiki install` copies the five skill directories into the Codex skills target.
- Installed skill directories include `.project-llm-wiki-install.json` markers.
- Reinstall updates marker-owned dirs; unmarked user paths remain protected.
- `--force` migrates old symlink installs to copied directories.
- `--uninstall` removes only marker-owned directories and preserves foreign paths.
- README and reference docs now describe copy-based install and temp clone cleanup.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests -p 'test_project_wiki_install.py'` - 8 tests OK.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests -p 'test_project_wiki_package.py'` - 24 tests OK.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests` - 155 tests in 264.306s, OK.
- `curl -fsSL file://$PWD/install.sh | CODEX_HOME=$tmp/codex PROJECT_LLM_WIKI_HOME=$tmp/project-llm-wiki bash` - installed copied dirs with markers into temp Codex home.
- `git diff --check` - clean.

## Notes

Live GitHub raw curl should be tested after this commit is pushed, because public raw content follows `origin/main`.
