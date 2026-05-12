# Phase 2: Init and Wiki Templates - Pattern Map

**Mapped:** 2026-05-13
**Files analyzed:** 13 source/generation targets
**Analogs found:** 11 / 13

## File Classification

| New/Modified File Or Target | Role | Data Flow | Closest Analog | Match Quality |
|-----------------------------|------|-----------|----------------|---------------|
| `skills/project-llm-wiki/scripts/project_wiki.py` | utility / CLI | request-response, file-I/O | `skills/project-llm-wiki/scripts/project_wiki.py` | exact surface, new behavior |
| `skills/project-llm-wiki/tests/test_project_wiki_package.py` | test | request-response, transform | `skills/project-llm-wiki/tests/test_project_wiki_package.py` | exact |
| `skills/project-llm-wiki/tests/test_project_wiki_init.py` or equivalent methods | test | request-response, file-I/O | `skills/project-llm-wiki/tests/test_project_wiki_package.py` | role-match |
| `skills/project-llm-wiki/assets/templates/README.md` | config / template docs | file-I/O, static content | `skills/project-llm-wiki/assets/templates/README.md` | exact |
| `skills/project-llm-wiki/assets/templates/llm-wiki/README.md` | template | file-I/O, static content | `skills/project-llm-wiki/assets/templates/README.md` | role-match |
| `skills/project-llm-wiki/assets/templates/llm-wiki/AGENTS.md` | config / template instructions | file-I/O, static content | `skills/project-llm-wiki/SKILL.md` | role-match |
| `skills/project-llm-wiki/assets/templates/llm-wiki/index.md` | template / navigation | file-I/O, transform | `skills/project-llm-wiki/references/command-surface.md` | partial |
| `skills/project-llm-wiki/assets/templates/llm-wiki/log.md` | template / log | file-I/O, append-oriented | `skills/project-llm-wiki/references/command-surface.md` | partial |
| `skills/project-llm-wiki/assets/templates/llm-wiki/raw/README.md` | template / policy | file-I/O, static content | `skills/project-llm-wiki/assets/templates/README.md` | role-match |
| `skills/project-llm-wiki/assets/templates/llm-wiki/raw/curated/README.md` | template / policy | file-I/O, static content | `skills/project-llm-wiki/assets/templates/README.md` | role-match |
| `skills/project-llm-wiki/assets/templates/llm-wiki/features/ideas.md` | template / capture page | file-I/O, static content | `.planning/phases/02-init-and-wiki-templates/02-CONTEXT.md` | planning-ref only |
| Generated `.llm-wiki/summaries/repo-overview.md` via `project_wiki.py` | utility / template generator | transform, file-I/O | `.planning/phases/02-init-and-wiki-templates/02-RESEARCH.md` example | research-ref only |
| Generated category `.gitkeep` placeholders via `project_wiki.py` | utility / placeholder generator | file-I/O | `.planning/phases/02-init-and-wiki-templates/02-CONTEXT.md` | planning-ref only |

## Pattern Assignments

### `skills/project-llm-wiki/scripts/project_wiki.py` (utility / CLI, request-response + file-I/O)

**Analog:** `skills/project-llm-wiki/scripts/project_wiki.py`

**Imports pattern** (lines 1-5):

```python
#!/usr/bin/env python3
import argparse
import pathlib
import sys
import textwrap
```

Apply this style: top-level stdlib imports only. Phase 2 may add stdlib imports such as `subprocess`, `dataclasses`, `typing`, or `tempfile` only when the implementation or tests need them; no third-party imports.

**Return-code pattern** (lines 11-13):

```python
def planned_command(name: str, phase: str) -> int:
    print(f"{name} is planned for {phase}")
    return 2
```

Copy the simple integer-return contract: handlers print concise status and return explicit process codes. Conflicts and non-git contexts should return nonzero; successful dry-run without conflicts can return zero unless planner deliberately chooses otherwise.

**Parser pattern** (lines 16-30):

```python
def build_parser():
    parser = argparse.ArgumentParser(
        prog="project-wiki",
        description="Repo-local .llm-wiki helper for Project LLM Wiki",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Phase 1 exposes the helper surface without mutating repositories.
            Later phases implement init, lint, query, and ingest behavior.
            """
        ),
    )
    parser.set_defaults(func=lambda _args: parser.print_help() or 0)

    subcommands = parser.add_subparsers(dest="command")
```

Add `init --dry-run` inside this existing parser. Keep other subcommands as planned-mode handlers.

**Subcommand dispatch pattern** (lines 37-49):

```python
init = subcommands.add_parser("init", help="planned project-wiki-init mode")
init.set_defaults(func=lambda _args: planned_command("project-wiki-init", "Phase 2"))
```

Replace only the `init` handler with real Phase 2 behavior. Leave `lint`, `query`, and `ingest` deferred.

**Main pattern** (lines 52-59):

```python
def main(argv: list[str] | None = None) -> int:
    _script_path = pathlib.Path(__file__)
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__": raise SystemExit(main())
```

Keep `main(argv)` testable and side-effect-light. Resolve package template paths from `__file__` or a nearby helper, not from process cwd.

**New behavior with no current code analog:** Git root resolution, parent-workspace refusal, preflight conflict detection, dry-run, and missing-only file creation. Use the researched architecture rather than inventing a separate command surface:

- `git rev-parse --show-toplevel` is locked by context lines 16-21.
- Preflight conflicts before writes is locked by context lines 38-42.
- Dry-run reporting without writes is locked by context line 42.
- Seed sources are only `README.md` and `AGENTS.md`, per context lines 31-37.

---

### `skills/project-llm-wiki/tests/test_project_wiki_package.py` (test, request-response + transform)

**Analog:** `skills/project-llm-wiki/tests/test_project_wiki_package.py`

**Imports and constants pattern** (lines 1-9):

```python
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "skills" / "project-llm-wiki"
```

Keep tests stdlib-only. Add `tempfile` and possibly `shutil` only if needed for clean Git repo fixtures.

**Helper subprocess pattern** (lines 11-18):

```python
class ProjectWikiPackageTests(unittest.TestCase):
    def run_helper(self, *args):
        return subprocess.run(
            [sys.executable, str(PACKAGE / "scripts" / "project_wiki.py"), *args],
            capture_output=True,
            text=True,
            check=False,
        )
```

Reuse this pattern for CLI assertions. For init fixture tests, extend it to accept `cwd=repo` or add a second helper rather than shelling through strings.

**Existing command tests pattern** (lines 38-55):

```python
def test_helper_help_exits_zero(self):
    result = self.run_helper("--help")

    self.assertEqual(0, result.returncode)
    self.assertIn("Repo-local .llm-wiki helper for Project LLM Wiki", result.stdout)
```

Use return-code and output assertions for `init`, `init --dry-run`, non-git failure, parent workspace refusal, and conflict failure.

**Import whitelist pattern** (lines 57-71):

```python
def test_helper_imports_only_allowed_modules(self):
    allowed = {"argparse", "pathlib", "sys", "textwrap"}
    script = (PACKAGE / "scripts" / "project_wiki.py").read_text()
    imported = set()

    for line in script.splitlines():
        if line.startswith("import "):
            module = line.removeprefix("import ").split()[0].split(".")[0]
            imported.add(module)
        elif line.startswith("from "):
            module = line.removeprefix("from ").split()[0].split(".")[0]
            imported.add(module)

    self.assertTrue(imported)
    self.assertLessEqual(imported, allowed)
```

Update `allowed` for Phase 2 stdlib imports. Preserve the top-level import scanner so dependency creep stays visible.

**Template content assertion pattern** (lines 73-76):

```python
template_readme = (PACKAGE / "assets" / "templates" / "README.md").read_text()

self.assertIn("Final .llm-wiki/ templates are implemented in Phase 2.", template_readme)
```

Copy this for raw policy, ideas page, index links, and generated `repo-overview.md` content assertions.

---

### `skills/project-llm-wiki/tests/test_project_wiki_init.py` or equivalent methods (test, request-response + file-I/O)

**Analog:** `skills/project-llm-wiki/tests/test_project_wiki_package.py`

Use a separate file if the init fixture tests grow beyond package-shape assertions. If kept in the existing test file, preserve the class/helper style above.

**Validation contract to implement** (`02-VALIDATION.md` lines 55-60):

```markdown
- [ ] `skills/project-llm-wiki/tests/test_project_wiki_init.py` or equivalent test methods for clean Git repo init, subdirectory root detection, parent workspace refusal, dry-run, conflicts, idempotency, and `git status --short` visibility.
- [ ] Existing import whitelist in `skills/project-llm-wiki/tests/test_project_wiki_package.py` updated for any new standard-library imports such as `subprocess`, `tempfile`, `dataclasses`, or `shutil`.
- [ ] Temporary Git repo fixture helper using `tempfile.TemporaryDirectory` and `git init`.
- [ ] Content assertions for `.llm-wiki/raw/README.md`, `.llm-wiki/raw/curated/README.md`, `.llm-wiki/features/ideas.md`, and `.llm-wiki/summaries/repo-overview.md`.
```

**Existing subprocess analog:** use `run_helper()` from test lines 11-18 and add cwd support. Avoid shell commands in tests; use argument lists.

---

### `skills/project-llm-wiki/assets/templates/README.md` (config / template docs, static file-I/O)

**Analog:** `skills/project-llm-wiki/assets/templates/README.md`

**Current ownership pattern** (lines 1-13):

```markdown
# Project LLM Wiki Templates

## Phase 1 Status

Final .llm-wiki/ templates are implemented in Phase 2.

This directory exists in Phase 1 so the package has a stable asset location before template content is designed and tested.

## Phase 2 Ownership

Phase 2 owns the final `.llm-wiki/` skeleton templates, idempotent init behavior, and raw source policy files.

Template changes must stay inside the Project LLM Wiki package boundary unless a later plan explicitly adds target repository initialization behavior.
```

Update this README from "Phase 1 Status" wording to an inventory/ownership reference once actual `llm-wiki/` templates exist.

**Safety wording to preserve** (lines 15-21):

```markdown
Templates must not contain secrets, customer data, logs, database exports, or generated dumps.

Templates must preserve the rule that current repo code wins over wiki notes.

Templates must keep durable project knowledge separate from `.planning/`, Linear, OMX, workflow files, pull requests, and other volatile task state.
```

Every new template should carry these boundaries in user-facing wording where relevant, especially raw policy pages and AGENTS guidance.

---

### `skills/project-llm-wiki/assets/templates/llm-wiki/*.md` (templates, static file-I/O)

**Analogs:** `skills/project-llm-wiki/assets/templates/README.md`, `skills/project-llm-wiki/SKILL.md`, `skills/project-llm-wiki/references/package-contract.md`, `skills/project-llm-wiki/references/command-surface.md`

Apply this assignment to:

- `skills/project-llm-wiki/assets/templates/llm-wiki/README.md`
- `skills/project-llm-wiki/assets/templates/llm-wiki/AGENTS.md`
- `skills/project-llm-wiki/assets/templates/llm-wiki/index.md`
- `skills/project-llm-wiki/assets/templates/llm-wiki/log.md`
- `skills/project-llm-wiki/assets/templates/llm-wiki/raw/README.md`
- `skills/project-llm-wiki/assets/templates/llm-wiki/raw/curated/README.md`
- `skills/project-llm-wiki/assets/templates/llm-wiki/features/ideas.md`

**Protocol/safety content source** (`SKILL.md` lines 21-25):

```markdown
Read the target repository's git root before writing .llm-wiki/.

Keep durable, validated project knowledge in `.llm-wiki/`. Do not store active task state in .llm-wiki/.

Trust current repo code over .llm-wiki/ when they disagree.
```

**Raw/source safety content source** (`SKILL.md` lines 39-43):

```markdown
## Safety Boundaries

Do not initialize `.llm-wiki/` in a multi-repo parent directory unless the parent is the intended git repository.

Do not store secrets, credentials, private customer data, auth tokens, full logs, database exports, generated dumps, or unvalidated task notes in `.llm-wiki/`.
```

**Package boundary source** (`package-contract.md` lines 11-17):

```markdown
## Package Boundary

The package owns skills/project-llm-wiki/ and all descendants.

Package-owned files include skill instructions, deterministic helper scripts, wiki templates, reference documents, and tests for the reusable Project LLM Wiki skill.

The package must keep durable project knowledge separate from active task state. `.llm-wiki/` is for curated project knowledge; `.planning/`, Linear, OMX, workflow files, and pull requests are for volatile execution state.
```

**Navigation/heading style source** (`command-surface.md` lines 11-29):

```markdown
### project-wiki-init

Planned mode for detecting the target repository's actual git root and creating an idempotent `.llm-wiki/` skeleton.

### project-wiki-lint

Planned mode for checking broken wikilinks, missing index entries, secret-looking content, oversized raw files, stale pages, and likely repo/wiki contradictions.
```

Use short heading sections, explicit purpose, what belongs, what does not belong, and example links. Do not turn templates into long documentation pages.

**Required skeleton source** (`02-CONTEXT.md` lines 23-29):

```markdown
- **D-07:** Create these initial files and directories: `README.md`, `AGENTS.md`, `index.md`, `log.md`, `raw/README.md`, `raw/curated/README.md`, `architecture/`, `domain/`, `decisions/`, `operations/`, `features/`, `summaries/`, and `raw/curated/`.
- **D-08:** Add `.gitkeep` to otherwise-empty category directories so the complete skeleton appears in `git status`.
- **D-09:** Add `.llm-wiki/features/ideas.md` and link it from `index.md`. This page is for durable but immature ideas; it is not a roadmap, backlog, or active task-state store.
- **D-10:** Initial pages should be short guidance templates: purpose, what belongs there, what does not belong there, and a few example links.
```

---

### Generated `.llm-wiki/summaries/repo-overview.md` (implemented in `project_wiki.py`, transform + file-I/O)

**Analog:** research example in `.planning/phases/02-init-and-wiki-templates/02-RESEARCH.md`

There is no implemented generator yet. Use the research pattern and keep it light: provenance, found/skipped source status, and source-of-truth warning only.

**Seed scope source** (`02-CONTEXT.md` lines 31-37):

```markdown
- **D-12:** Seed with light summary plus provenance only. Do not attempt deep interpretation during init.
- **D-13:** Phase 2 may read only `README.md` and `AGENTS.md` for seed content. These are human-authored orientation/instruction files.
- **D-14:** Do not seed wiki content from language manifests or config files such as `package.json`, `pyproject.toml`, `go.mod`, or `Cargo.toml`.
- **D-15:** Write seeded content to `.llm-wiki/summaries/repo-overview.md` and link it from `index.md`.
- **D-16:** If `README.md` or `AGENTS.md` is missing, init should still create the skeleton and report the source as skipped.
```

**Research code shape** (`02-RESEARCH.md` lines 438-467):

```python
def build_repo_overview(readme_found: bool, agents_found: bool) -> str:
    sources = []
    skipped = []
    if readme_found:
        sources.append("README.md")
    else:
        skipped.append("README.md")
    if agents_found:
        sources.append("AGENTS.md")
    else:
        skipped.append("AGENTS.md")

    return "\n".join(
        [
            "# Repo Overview",
            "",
            "This page was seeded during project-wiki-init.",
            "",
            f"Sources found: {', '.join(sources) if sources else 'none'}",
            f"Sources skipped: {', '.join(skipped) if skipped else 'none'}",
            "",
            "Current repository files are authoritative when they disagree with this wiki.",
            "",
        ]
    )
```

Planner should decide whether this generated page lives entirely in code or uses a small template helper. Do not create a static `repo-overview.md` asset that pretends source availability is fixed.

---

### Generated category `.gitkeep` placeholders (implemented in `project_wiki.py`, file-I/O)

**Analog:** no content analog; requirement source is `02-CONTEXT.md`.

Apply to otherwise-empty category directories only:

- `.llm-wiki/architecture/.gitkeep`
- `.llm-wiki/domain/.gitkeep`
- `.llm-wiki/decisions/.gitkeep`
- `.llm-wiki/operations/.gitkeep`

Do not add `.gitkeep` to directories that receive required files during init, such as `features/`, `summaries/`, `raw/`, or `raw/curated/`.

## Shared Patterns

### Standard-Library-Only Runtime

**Source:** `skills/project-llm-wiki/scripts/project_wiki.py` lines 1-5 and `skills/project-llm-wiki/references/testing.md` lines 19-23

```markdown
## No Dependency Rule

The helper script may import argparse, pathlib, sys, and textwrap only in Phase 1.

Tests should use Python standard-library modules only.
```

Phase 2 should update the whitelist but keep the rule: stdlib plus Git CLI, no new dependency.

### Actual Git Root Before Writes

**Source:** `skills/project-llm-wiki/SKILL.md` lines 21-25 and `02-CONTEXT.md` lines 16-21

```markdown
Read the target repository's git root before writing .llm-wiki/.
```

All init path planning must be rooted at `git rev-parse --show-toplevel`. Do not implement `--target` in Phase 2.

### Existing File Preservation

**Source:** `02-CONTEXT.md` lines 38-42

```markdown
- **D-17:** Re-running init must never overwrite existing files. It only creates missing files/directories and reports skipped paths.
- **D-18:** If an existing `.llm-wiki/index.md` is missing links to new default pages, init must not edit it.
- **D-19:** If a required directory path is occupied by a file, init must fail before partial writes and list each conflict with the expected path type.
- **D-20:** Support `--dry-run`; it reports would-create, would-skip, and conflicts without writing files.
```

Build a plan first, preflight every path, then apply missing-only operations.

### Raw Source Policy

**Source:** `02-CONTEXT.md` lines 44-49 and `skills/project-llm-wiki/assets/templates/README.md` lines 15-21

```markdown
Templates must not contain secrets, customer data, logs, database exports, or generated dumps.

Templates must preserve the rule that current repo code wins over wiki notes.
```

Raw policy templates must warn clearly but not claim Phase 3 secret scanning exists yet.

### Automated Verification

**Source:** `02-VALIDATION.md` lines 16-24 and 28-33

```markdown
| **Framework** | Python `unittest` with standard-library subprocess and temporary Git repo fixtures |
| **Quick run command** | `python3 -m unittest discover -s skills/project-llm-wiki/tests` |

- **After every task commit:** Run `python3 -m unittest discover -s skills/project-llm-wiki/tests`
```

Every implementation slice should keep this command green.

## No Analog Found

| File / Behavior | Role | Data Flow | Reason |
|-----------------|------|-----------|--------|
| Git-root resolver in `project_wiki.py` | utility | request-response | No existing helper invokes Git; use research pattern and `subprocess.run([...], shell=False)`. |
| Init preflight/dry-run/apply plan in `project_wiki.py` | utility | file-I/O | No current no-overwrite planner exists; implement from context decisions D-17 through D-20. |
| Parent workspace child repo discovery | utility | file-I/O, request-response | Context allows candidate listing but no local code decides search depth; keep shallow and concise unless planner locks more. |
| `features/ideas.md` template | template | static content | No existing idea-capture template; use context lines 104-106 for fields and keep it out of roadmap/backlog semantics. |
| `.gitkeep` generation | utility / placeholder | file-I/O | No existing placeholder generator; create only for otherwise-empty required category directories. |

## Metadata

**Analog search scope:** `skills/project-llm-wiki/`, `.planning/phases/01-skill-package-foundation/`, `.planning/phases/02-init-and-wiki-templates/`, root `AGENTS.md`, root `README.md`

**Files scanned:** 8 package/root source files plus 6 phase planning files

**Strong analogs used:** 5 (`project_wiki.py`, `test_project_wiki_package.py`, `assets/templates/README.md`, `SKILL.md`, `package-contract.md`)

**Pattern extraction date:** 2026-05-13
