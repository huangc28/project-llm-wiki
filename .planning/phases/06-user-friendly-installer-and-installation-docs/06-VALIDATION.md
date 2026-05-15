# Phase 6: User-Friendly Installer and Installation Docs - Validation

**Created:** 2026-05-15
**Status:** Ready

## Validation Architecture

Phase 6 passes only when installation is easy for users and safe for local filesystems.

## Required Evidence

- `project_wiki.py install --help` documents `--target`, `--dry-run`, `--force`, and `--uninstall`.
- Unit tests prove install creates exactly the five expected Codex skill links in a temporary target.
- Unit tests prove dry-run and conflict cases do not write partial installs.
- Unit tests prove install and init write boundaries stay separate.
- README quick start starts with the one-line curl installer and `$project-wiki-init`.

## Acceptance Commands

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests -p "test_project_wiki_install.py"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests
rg -n "curl -fsSL https://raw.githubusercontent.com/huangc28/project-llm-wiki/main/install.sh \\| bash|Restart Codex|\\$project-wiki-init" README.md
```

