# Phase 6: User-Friendly Installer and Installation Docs - Research

**Researched:** 2026-05-15
**Domain:** User-friendly CLI installation, Codex skill package installation, Python stdlib filesystem safety
**Confidence:** HIGH

## Summary

The best v1 shape is a two-layer installer:

- Public UX: one `curl .../install.sh | bash` command in README.
- Core behavior: `project_wiki.py install`, implemented in Python stdlib and covered by unit tests.

This preserves both priorities: ordinary users get a direct install command, while risky filesystem behavior remains deterministic and testable.

## Option Comparison

| Option | UX | Safety/Testability | Decision |
| --- | --- | --- | --- |
| `curl | bash` only | Best | Weak if logic lives in shell | Use as thin bootstrap only |
| `project_wiki.py install` only | Moderate | Best | Use as core implementation |
| Standalone Python installer | Moderate | Good | Reject as duplicate CLI surface |
| Codex skill-installer GitHub path | Good for Codex users | Depends on Codex installer behavior | Document as possible later alternative, not v1 primary |
| npm/pip package | Familiar to some users | Adds release/dependency overhead | Defer |

## Recommended Architecture

```text
install.sh
  -> clone/update package into ${PROJECT_LLM_WIKI_HOME:-~/.local/share/project-llm-wiki}
  -> python3 skills/project-llm-wiki/scripts/project_wiki.py install

project_wiki.py install
  -> validate package contains all five skill dirs
  -> validate target ${CODEX_HOME:-~/.codex}/skills
  -> create/update symlinks safely
  -> support --dry-run, --force, --uninstall, --target

$project-wiki-init
  -> unchanged target-repo initialization path
```

## Safety Findings

- Installation must not call `project-wiki init`.
- The install target should default to `${CODEX_HOME:-~/.codex}/skills`.
- If `${CODEX_HOME:-~/.codex}` does not exist, fail clearly instead of inventing a Codex home.
- Existing real directories under the skill target must be conflicts.
- Symlink replacement is safe only when the existing entry is a symlink and `--force` is present.
- `--uninstall` must remove only symlinks that resolve into this package directory.

## Test Strategy

Use `unittest`, `tempfile`, and subprocess calls matching the existing package tests. Tests should avoid touching the real `~/.codex` by always passing `--target` or setting `CODEX_HOME` to a temporary directory.

The core tests should prove:

- five expected skills are installed
- second install is idempotent
- dry-run writes nothing
- real directory conflicts abort before partial writes
- stale symlink replacement requires `--force`
- uninstall removes only owned links
- install never creates `.llm-wiki/` or modifies root `AGENTS.md`

## Documentation Strategy

README should optimize for the user mental model:

```text
Install once:
  curl -fsSL https://raw.githubusercontent.com/huangc28/project-llm-wiki/main/install.sh | bash

Restart Codex.

Use in any repo:
  $project-wiki-init
```

All clone/manual symlink/Python fallback instructions belong below that as advanced troubleshooting.

## Risks

- `curl | bash` can feel opaque; mitigate by keeping `install.sh` small and readable.
- Symlink behavior differs on some systems; this repo currently targets the user's macOS/Codex environment, and tests can skip symlink-specific assertions only if the OS denies symlink creation.
- Existing manual installs may have real directories in `~/.codex/skills`; refuse rather than silently replacing.

