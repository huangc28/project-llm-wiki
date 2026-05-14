# Phase 5: Agent Instructions and Real Repo Validation - Pattern Map

**Mapped:** 2026-05-14
**Files analyzed:** 7
**Analogs found:** 7 / 7

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `skills/project-llm-wiki/scripts/project_wiki.py` | utility / CLI service | file-I/O, request-response, transform | `skills/project-llm-wiki/scripts/project_wiki.py` init helpers | exact for init flow, role-match for new AGENTS patch helper |
| `skills/project-llm-wiki/tests/test_project_wiki_init.py` | test | file-I/O, request-response, subprocess | `skills/project-llm-wiki/tests/test_project_wiki_init.py` existing init tests | exact |
| `skills/project-llm-wiki/tests/test_project_wiki_package.py` | test | request-response, static-doc assertion | `skills/project-llm-wiki/tests/test_project_wiki_package.py` docs/help/import tests | exact |
| `skills/project-llm-wiki/SKILL.md` | documentation / skill protocol | static protocol | `skills/project-llm-wiki/SKILL.md` existing mode protocol | role-match |
| `skills/project-llm-wiki/references/command-surface.md` | documentation / command contract | static protocol | `skills/project-llm-wiki/references/command-surface.md` current mode sections | exact |
| `skills/project-llm-wiki/references/testing.md` | documentation / validation contract | static protocol | `skills/project-llm-wiki/references/testing.md` Phase 2-4 validation sections | exact |
| `.planning/phases/05-agent-instructions-and-real-repo-validation/05-ROLLOUT-REPORT.md` | report / validation artifact | batch, smoke, file-I/O evidence | `.planning/phases/04-query-and-ingest-loop/04-VERIFICATION.md` | role-match |

## Pattern Assignments

### `skills/project-llm-wiki/scripts/project_wiki.py` (utility / CLI service, file-I/O + request-response)

**Analog:** `skills/project-llm-wiki/scripts/project_wiki.py`

**Imports pattern** (lines 2-9):

```python
import argparse
import datetime
import json
import pathlib
import re
import subprocess
import sys
import textwrap
```

Use only Python standard-library imports. If a new stdlib import is truly needed, update the import whitelist test in `test_project_wiki_package.py`; otherwise keep AGENTS patching on `pathlib`, `re`, `textwrap`, and normal file APIs already imported.

**Constant and path contract pattern** (lines 12-45):

```python
VERSION = "0.1.0-foundation"
WIKI_ROOT = pathlib.Path(".llm-wiki")
REQUIRED_DIRECTORIES = tuple(
    pathlib.Path(path)
    for path in (
        ".llm-wiki",
        ".llm-wiki/raw",
        ".llm-wiki/raw/curated",
        ".llm-wiki/architecture",
        ".llm-wiki/domain",
        ".llm-wiki/decisions",
        ".llm-wiki/operations",
        ".llm-wiki/features",
        ".llm-wiki/summaries",
    )
)
REQUIRED_FILES = tuple(
    pathlib.Path(path)
    for path in (
        ".llm-wiki/README.md",
        ".llm-wiki/AGENTS.md",
        ".llm-wiki/index.md",
        ".llm-wiki/log.md",
        ".llm-wiki/raw/README.md",
        ".llm-wiki/raw/curated/README.md",
        ".llm-wiki/features/ideas.md",
        ".llm-wiki/summaries/repo-overview.md",
        ".llm-wiki/architecture/.gitkeep",
        ".llm-wiki/domain/.gitkeep",
        ".llm-wiki/decisions/.gitkeep",
        ".llm-wiki/operations/.gitkeep",
    )
)
RECOMMENDED_INDEX_LINKS = ("[[features/ideas]]", "[[summaries/repo-overview]]")
```

Add root `AGENTS.md` marker constants near these top-level constants. Do not add root `AGENTS.md` to `REQUIRED_FILES`, because it is not part of the `.llm-wiki/` skeleton and has separate conflict semantics.

**Git-root boundary pattern** (lines 149-160):

```python
def resolve_git_root(cwd: pathlib.Path) -> tuple[pathlib.Path | None, str | None]:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0 and result.stdout.strip():
        return pathlib.Path(result.stdout.strip()), None
    message = result.stderr.strip() or "not inside a Git worktree"
    return None, message
```

All AGENTS patch planning must use the same `git_root` returned by `resolve_git_root`. Do not add a `--target` escape hatch.

**Template/content generation pattern** (lines 184-239):

```python
def load_template_contents() -> tuple[dict[str, str], list[str]]:
    root = template_root()
    contents: dict[str, str] = {}
    missing: list[str] = []
    for target_path in TEMPLATE_FILES:
        template_relative_path = target_path.relative_to(WIKI_ROOT)
        template_path = root / template_relative_path
        if template_path.is_file():
            contents[target_path.as_posix()] = template_path.read_text(
                encoding="utf-8"
            )
        else:
            missing.append(template_relative_path.as_posix())
    return contents, missing
```

```python
def build_init_file_contents(
    repo_root: pathlib.Path, template_contents: dict[str, str]
) -> tuple[dict[str, str], list[str], list[str]]:
    repo_overview, found_sources, skipped_sources = build_repo_overview(repo_root)
    contents = dict(template_contents)
    contents[".llm-wiki/summaries/repo-overview.md"] = repo_overview
    contents[".llm-wiki/architecture/.gitkeep"] = ""
    contents[".llm-wiki/domain/.gitkeep"] = ""
    contents[".llm-wiki/decisions/.gitkeep"] = ""
    contents[".llm-wiki/operations/.gitkeep"] = ""
    return contents, found_sources, skipped_sources
```

Root `AGENTS.md` section rendering should follow the same pure-computation style: build a deterministic section string before writing, then pass a plan to dry-run or apply paths.

**Root confinement pattern** (lines 242-247):

```python
def path_is_under(path: pathlib.Path, root: pathlib.Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve())
    except ValueError:
        return False
    return True
```

Use this style for any path guard that checks root-confined writes. The AGENTS target should be exactly `git_root / "AGENTS.md"`.

**Conflict preflight pattern** (lines 745-771):

```python
def find_init_conflicts(git_root: pathlib.Path) -> list[str]:
    conflicts: list[str] = []
    for relative_path in REQUIRED_DIRECTORIES:
        path = git_root / relative_path
        if path.is_symlink():
            conflicts.append(
                f"{relative_path.as_posix()}: expected real directory, found symlink"
            )
        elif path.exists() and not path.is_dir():
            conflicts.append(
                f"{relative_path.as_posix()}: expected directory, found file"
            )
        elif path.exists() and not path_is_under(path, git_root):
            conflicts.append(f"{relative_path.as_posix()}: resolves outside git root")
    for relative_path in REQUIRED_FILES:
        path = git_root / relative_path
        if path.is_symlink():
            conflicts.append(
                f"{relative_path.as_posix()}: expected real file, found symlink"
            )
        elif path.exists() and not path.is_file():
            conflicts.append(
                f"{relative_path.as_posix()}: expected file, found directory"
            )
        elif path.exists() and not path_is_under(path, git_root):
            conflicts.append(f"{relative_path.as_posix()}: resolves outside git root")
    return conflicts
```

Add AGENTS-specific conflict detection as a separate helper rather than mixing marker logic into `.llm-wiki/` skeleton conflicts. It should return conflict strings for invalid UTF-8, unmatched start/end markers, duplicate marker pairs, symlinked root `AGENTS.md`, and non-file root `AGENTS.md`.

**Plan/apply/output pattern** (lines 786-849):

```python
def collect_init_paths(
    git_root: pathlib.Path,
) -> tuple[list[pathlib.Path], list[pathlib.Path]]:
    create: list[pathlib.Path] = []
    skip: list[pathlib.Path] = []
    for relative_path in (*REQUIRED_DIRECTORIES, *REQUIRED_FILES):
        if (git_root / relative_path).exists():
            skip.append(relative_path)
        else:
            create.append(relative_path)
    return create, skip
```

```python
def create_file_if_missing(path: pathlib.Path, content: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True
```

```python
def print_path_section(heading: str, paths: list[pathlib.Path]) -> None:
    print(heading)
    if not paths:
        print("- (none)")
        return
    for path in paths:
        print(f"- {path.as_posix()}")
```

Create an `AgentsPatchPlan`-style value or simple tuple/dict that describes `action`, `path`, `content`, and `conflicts`. Use the same object for dry-run display and apply so the two paths cannot diverge.

**Dry-run and apply control-flow pattern** (lines 1503-1562):

```python
def run_init(args) -> int:
    cwd = pathlib.Path.cwd()
    git_root, _message = resolve_git_root(cwd)
    if git_root is None:
        print("No git repository found for current directory.")
        candidates = find_candidate_child_repos(cwd)
        if candidates:
            print("Candidate child repositories:")
            for candidate in candidates:
                print(f"- {candidate.relative_to(cwd)}")
        print("Next: cd into the intended repo before running project-wiki init")
        return 2

    print(f"Resolved git root: {git_root}")
    conflicts = find_init_conflicts(git_root)
    template_contents, missing_templates = load_template_contents()
    file_contents, found_sources, skipped_sources = build_init_file_contents(
        git_root, template_contents
    )
    would_create, would_skip = collect_init_paths(git_root)
    if args.dry_run:
        print_path_section("Would create paths:", would_create)
        print_path_section("Would skip existing paths:", would_skip)
        print_source_status(found_sources, skipped_sources)
        if conflicts:
            print_text_section("Conflicts:", conflicts)
            return 2
        if missing_templates:
            print_text_section("Template assets missing:", missing_templates)
            return 2
```

Extend this flow by computing AGENTS patch planning before the `if args.dry_run` branch. In dry-run, print the AGENTS action and exact managed section. In apply, return `2` before any writes if either skeleton conflicts or AGENTS conflicts exist.

**Parser pattern** (lines 1565-1595):

```python
def build_parser():
    parser = argparse.ArgumentParser(
        prog="project-wiki",
        description="Repo-local .llm-wiki helper for Project LLM Wiki",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            project-wiki init creates a .llm-wiki skeleton in the current Git root.
            Use project-wiki init --dry-run to preview changes without writing files.
            query prepares index-first support packets; ingest updates curated wiki pages.
            """
        ),
    )
```

```python
init = subcommands.add_parser(
    "init", help="initialize .llm-wiki in the current Git repo"
)
init.add_argument(
    "--dry-run",
    action="store_true",
    help="report planned changes without writing files",
)
init.set_defaults(func=run_init)
```

Add `--no-patch-agents` on the `init` parser. Keep it as an opt-out flag; do not add an opt-in `--patch-agents` default.

**Managed section template source** (`05-RESEARCH.md` lines 302-315):

```text
<!-- PROJECT-LLM-WIKI:START -->
## Project LLM Wiki

Before non-trivial architecture, debugging, product, onboarding, or cross-file implementation work, read `.llm-wiki/index.md` first, then only task-relevant linked pages.

For simple typo fixes and narrow single-file edits, wiki lookup is not required.

Current repository files are authoritative when they disagree with `.llm-wiki/`; report wiki drift when found.

Update `.llm-wiki/` only after validated non-trivial work produces durable learning. Do not use `.llm-wiki/` for active task status.
<!-- PROJECT-LLM-WIKI:END -->
```

Use this exact marker shape. The wording can be held as a Python constant for Phase 5 unless the planner chooses an asset file.

---

### `skills/project-llm-wiki/tests/test_project_wiki_init.py` (test, subprocess + file-I/O)

**Analog:** `skills/project-llm-wiki/tests/test_project_wiki_init.py`

**Imports and helper pattern** (lines 1-50):

```python
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "skills" / "project-llm-wiki"
HELPER = PACKAGE / "scripts" / "project_wiki.py"
```

```python
def run_helper(self, cwd: Path, *args: str):
    return subprocess.run(
        [sys.executable, str(HELPER), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
```

New tests should invoke the CLI through `run_helper`, not import helper internals. For byte-level AGENTS assertions, read files with `read_bytes()` in the test body.

**Clean init fixture pattern** (lines 52-84):

```python
def test_init_creates_wiki_at_git_root_from_subdirectory(self):
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        self.init_repo(repo)
        (repo / "README.md").write_text("# Test Repo\n", encoding="utf-8")
        (repo / "AGENTS.md").write_text("# Agent Instructions\n", encoding="utf-8")
        nested = repo / "nested" / "deeper"
        nested.mkdir(parents=True)

        result = self.run_helper(nested, "init")
        output = result.stdout + result.stderr

        self.assertEqual(0, result.returncode, output)
```

Follow this pattern for root `AGENTS.md` insertion from a nested directory: create a temp Git repo, run `init`, inspect the actual root file, and assert no nested `.llm-wiki/`.

**Dry-run no-write pattern** (lines 102-117):

```python
def test_dry_run_reports_without_writing(self):
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        self.init_repo(repo)
        (repo / "README.md").write_text("# Test Repo\n", encoding="utf-8")

        result = self.run_helper(repo, "init", "--dry-run")
        output = result.stdout + result.stderr

        self.assertEqual(0, result.returncode, output)
        self.assertFalse((repo / ".llm-wiki").exists())
        self.assertIn("Resolved git root:", output)
        self.assertIn("Would create paths:", output)
```

Extend this with `AGENTS.md` checks: capture `before = agents_path.read_bytes()` when the file exists, assert dry-run prints `Managed AGENTS.md section:`, and assert bytes are unchanged or missing file remains absent.

**Conflict-before-partial-write pattern** (lines 118-149):

```python
def test_conflict_fails_before_partial_writes(self):
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        self.init_repo(repo)
        wiki = repo / ".llm-wiki"
        wiki.mkdir()
        (wiki / "features").write_text("not a directory\n", encoding="utf-8")

        result = self.run_helper(repo, "init")
        output = result.stdout + result.stderr

        self.assertNotEqual(0, result.returncode)
        self.assertIn(".llm-wiki/features: expected directory, found file", output)
        self.assertFalse((wiki / "README.md").exists())
```

AGENTS marker conflicts should use the same shape: invalid marker state returns non-zero, prints conflict/remediation text, does not create `.llm-wiki/` partial content, and leaves root `AGENTS.md` unchanged.

**Invalid UTF-8 and no-traceback pattern** (lines 205-243):

```python
def test_init_rejects_invalid_existing_index_before_writing(self):
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        self.init_repo(repo)
        wiki = repo / ".llm-wiki"
        wiki.mkdir()
        (wiki / "index.md").write_bytes(b"\xff\xfeinvalid index\n")

        result = self.run_helper(repo, "init")
        output = result.stdout + result.stderr

        self.assertEqual(2, result.returncode, output)
        self.assertIn(
            ".llm-wiki/index.md: expected UTF-8 markdown, could not read",
            output,
        )
        self.assertNotIn("Traceback", output)
```

Mirror this for invalid UTF-8 root `AGENTS.md`. The expected behavior is a controlled conflict, not a traceback and not guessed encoding repair.

**Rerun/idempotency pattern** (lines 267-290):

```python
def test_rerun_preserves_existing_files_and_reports_missing_index_links(self):
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        self.init_repo(repo)

        first = self.run_helper(repo, "init")
        first_output = first.stdout + first.stderr
        self.assertEqual(0, first.returncode, first_output)

        index = repo / ".llm-wiki" / "index.md"
        overview = repo / ".llm-wiki" / "summaries" / "repo-overview.md"
        index.write_text("# Custom Index\n\nSentinel\n", encoding="utf-8")
        overview.write_text("# Custom Overview\n\nSentinel\n", encoding="utf-8")

        rerun = self.run_helper(repo, "init")
        output = rerun.stdout + rerun.stderr

        self.assertEqual(0, rerun.returncode, output)
        self.assertIn("Sentinel", index.read_text(encoding="utf-8"))
```

Add an AGENTS rerun test that starts with an existing marker-bounded section, reruns `init`, and asserts only the marker-bounded section changes.

**Byte-preservation target fixture model** (`peasydeal_be/AGENTS.md` lines 1-44):

```markdown
# Agent Instructions

## NotebookLM Second Brain

This project uses NotebookLM as a long-term knowledge base for Codex and other agents.
```

```markdown
Workflow:
1. Query NotebookLM for stable, curated context.
2. Inspect the local repository to verify the current implementation.
3. If NotebookLM and the repository disagree, treat the repository as the source of truth.
4. Mention important mismatches briefly.
5. After implementing a non-trivial feature or workflow change, update the project notebook if validation succeeds.
```

Use a local temp-file fixture modeled on this, not writes to `peasydeal_be`. Assert marker-external bytes remain identical.

---

### `skills/project-llm-wiki/tests/test_project_wiki_package.py` (test, help/docs/import contract)

**Analog:** `skills/project-llm-wiki/tests/test_project_wiki_package.py`

**Helper pattern** (lines 12-19):

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

Use this helper to add `init --help` assertions for `--no-patch-agents`.

**Help-output assertion pattern** (lines 74-90):

```python
def test_helper_help_exits_zero(self):
    result = self.run_helper("--help")

    self.assertEqual(0, result.returncode)
    self.assertIn("Repo-local .llm-wiki helper for Project LLM Wiki", result.stdout)
```

```python
def test_lint_help_documents_json_flag(self):
    result = self.run_helper("lint", "--help")

    self.assertEqual(0, result.returncode)
    self.assertIn("--json", result.stdout)
```

Add a focused init-help test rather than expanding unrelated help tests too much.

**Documentation contract test pattern** (lines 123-151):

```python
def test_command_surface_documents_completed_query_and_ingest_contract(self):
    command_surface = (PACKAGE / "references" / "command-surface.md").read_text()

    for expected in (
        "Implemented support mode for reading `.llm-wiki/index.md` first",
        "project-wiki query QUESTION",
        "project-wiki query QUESTION --consulted PAGE --key-insight TEXT",
        "Implemented mode for updating existing wiki pages",
        "project-wiki ingest --text TEXT --title TITLE --target-page PAGE --key-idea TEXT",
    ):
        self.assertIn(expected, command_surface)
    self.assertNotIn("Query and ingest loop: Phase 4", command_surface)
```

Add Phase 5 assertions that `command-surface.md` documents default AGENTS patching, `--no-patch-agents`, dry-run managed-section output, and no longer lists AGENTS integration as deferred.

**Testing reference assertion pattern** (lines 153-183):

```python
def test_testing_reference_documents_phase_4_validation_contract(self):
    testing_reference = (PACKAGE / "references" / "testing.md").read_text()

    for expected in (
        "Phase 4 Validation Contract",
        "test_project_wiki_query.py",
        "test_project_wiki_ingest.py",
        "QUERY-01",
        "QUERY-04",
        "INGEST-01",
        "INGEST-05",
        "TEST-03",
        "video sources require transcript, summary, or curated notes",
    ):
        self.assertIn(expected, testing_reference)
```

Mirror this with `"Phase 5 Validation Contract"`, `TEST-06`, `TEST-07`, `--no-patch-agents`, marker conflicts, and `peasydeal_be` dry-run report.

**Import whitelist pattern** (lines 207-230):

```python
def test_helper_imports_only_allowed_modules(self):
    allowed = {
        "argparse",
        "datetime",
        "json",
        "pathlib",
        "re",
        "subprocess",
        "sys",
        "textwrap",
    }
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

Keep Phase 5 implementation inside the existing allowed set unless there is a strong reason to add another stdlib module.

---

### `skills/project-llm-wiki/SKILL.md` (documentation / skill protocol, static)

**Analog:** `skills/project-llm-wiki/SKILL.md`

**Trigger and protocol pattern** (lines 8-25):

```markdown
## Trigger

Use this skill when the user asks to create, initialize, query, lint, ingest, or maintain a repo-local Project LLM Wiki.

Recognized trigger phrases:

- `project-wiki-init`
- `project-wiki-lint`
- `project-wiki-query`
- `project-wiki-ingest`
```

```markdown
Read the target repository's git root before writing .llm-wiki/.

Keep durable, validated project knowledge in `.llm-wiki/`. Do not store active task state in .llm-wiki/.

Trust current repo code over .llm-wiki/ when they disagree.
```

If this file is updated, keep it protocol-level. Mention that init patches root `AGENTS.md` by default when safe and that `--no-patch-agents` opts out, but do not duplicate the entire root managed section.

**Mode description pattern** (lines 29-35):

```markdown
## Modes

`project-wiki-init` creates the initial `.llm-wiki/` skeleton in the target repository's actual git root. Full behavior is implemented in Phase 2.

`project-wiki-lint` checks wiki structure, safety, freshness, and repo/wiki drift. Full behavior is implemented in Phase 3.

`project-wiki-query` answers from `.llm-wiki/index.md` and related pages with repo-local wikilink citations.
```

Update the init description only if package/docs tests require the skill to reflect Phase 5. Keep query/ingest wording stable.

**Quality check pattern** (lines 74-76):

```markdown
## Quality Check

Run `python3 -m unittest discover -s skills/project-llm-wiki/tests` after package changes.
```

No new runtime dependency or external service check belongs here for Phase 5.

---

### `skills/project-llm-wiki/references/command-surface.md` (documentation / command contract, static)

**Analog:** `skills/project-llm-wiki/references/command-surface.md`

**Mode-section pattern** (lines 1-14):

```markdown
# Command Surface

## Current Contract

The package documents mode names and boundaries for the reusable Project LLM Wiki skill. Implemented modes are safe to run through the helper script; deferred modes remain documented so future phases do not change command names accidentally.

The reusable package exposes one `project-llm-wiki` skill plus thin alias skills for the implemented mode triggers. The alias skills exist so Codex can show `$project-wiki-*` entries in skill autocomplete while keeping the detailed protocol in `project-llm-wiki`.

## Modes

### project-wiki-init

Implemented mode for detecting the current repository's actual Git root and creating an idempotent `.llm-wiki/` skeleton.
```

Extend the `project-wiki-init` section in place. Add examples for `project-wiki init`, `project-wiki init --dry-run`, and `project-wiki init --no-patch-agents`. State that root `AGENTS.md` patching is default when safe.

**Implemented-mode example pattern** (lines 47-67):

```markdown
### project-wiki-query

Implemented support mode for reading `.llm-wiki/index.md` first, preparing candidate repo-local wiki pages, and appending bounded query history to `.llm-wiki/log.md`.

Prepare a human-readable support packet:

`project-wiki query QUESTION`

Prepare a parseable support packet:

`project-wiki query QUESTION --json`
```

Use this concise shape for init examples. Do not add a long policy dump; point at managed-section behavior and conflict states.

**Alias/deferred pattern** (lines 101-121):

```markdown
## Alias Skills

Implemented thin aliases:

- `$project-wiki-init`
- `$project-wiki-lint`
- `$project-wiki-query`
- `$project-wiki-ingest`
```

```markdown
## Deferred Behavior

Full command behavior is deferred to later phases:

- Promotion of validated learnings into `.llm-wiki/`
- AGENTS integration and real repo validation: Phase 5
```

Remove the Phase 5 deferred bullet once implementation/docs land. Promotion remains deferred.

---

### `skills/project-llm-wiki/references/testing.md` (documentation / validation contract, static)

**Analog:** `skills/project-llm-wiki/references/testing.md`

**Command list pattern** (lines 3-19):

```markdown
## Test Commands

Run package tests with:

`python3 -m unittest discover -s skills/project-llm-wiki/tests`

Run the targeted Phase 3 lint suite with:

`python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_lint.py`
```

Add the targeted Phase 5 init suite command near the other targeted commands:
`python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_init.py`.

**Validation contract pattern** (lines 21-37):

```markdown
## Phase 2 Validation Contract

Phase 2 tests verify the init behavior before production implementation turns the
suite green. The Wave 0 validation fixtures use clean temporary Git repositories
so init behavior is tested through the same subprocess boundary users will run.

The validation suite covers:

- Git-root initialization from clean temporary Git repositories and nested
  subdirectories.
- `git status --short` visibility for generated `.llm-wiki/` files.
- `init --dry-run` reporting without filesystem side effects.
- idempotency for reruns that must preserve existing wiki notes.
- Conflict preflight before partial writes.
```

Add a Phase 5 section following this style. Cover AGENTS insertion/update, dry-run no-write, `--no-patch-agents`, invalid UTF-8, unmatched/duplicate markers, missing root `AGENTS.md`, byte-preservation fixtures, and `peasydeal_be` dry-run report.

**No-dependency pattern** (lines 104-110):

```markdown
## No Dependency Rule

The helper script should stay on the Python standard library. The import
whitelist test must be updated only when `project_wiki.py` actually imports a new
standard-library module.

Tests should use Python standard-library modules only.
```

Keep this unchanged unless implementation imports another stdlib module.

---

### `.planning/phases/05-agent-instructions-and-real-repo-validation/05-ROLLOUT-REPORT.md` (report, batch/smoke evidence)

**Analog:** `.planning/phases/04-query-and-ingest-loop/04-VERIFICATION.md`

**Report frontmatter and status pattern** (`04-VERIFICATION.md` lines 1-21):

```markdown
---
phase: 04-query-and-ingest-loop
verified: 2026-05-13T10:36:17Z
status: human_needed
score: "24/24 must-haves verified"
overrides_applied: 0
human_verification:
  - test: "Agent-authored final query answer quality"
    expected: "Given seeded wiki pages, the final agent answer uses direct [[wikilink]] citations, labels inference separately, and returns not-covered instead of guessing when evidence is absent."
    why_human: "Phase 4 deliberately keeps semantic final-answer generation out of Python; automated tests verify index-first support packets, citation contract text, and logging, not the actual LLM-authored answer."
---

# Phase 4: Query and Ingest Loop Verification Report

**Phase Goal:** Implement the repo-local compounding wiki loop: query with citations and ingest curated sources into existing pages first.
**Verified:** 2026-05-13T10:36:17Z
**Status:** human_needed
```

For the rollout report, use status values aligned to the locked verdict: `PASS`, `FLAG`, or `BLOCK`. Include `verdict:` in frontmatter and repeat it visibly in the body.

**Evidence table pattern** (`04-VERIFICATION.md` lines 91-103):

```markdown
### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Query behavior | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_query.py` | Ran 16 tests in 3.818s, OK. | PASS |
| Ingest behavior | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_ingest.py` | Ran 30 tests in 8.437s, OK. | PASS |
| Package/help/docs/imports | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_package.py` | Ran 15 tests in 0.409s, OK. | PASS |
| Full package suite | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests` | Ran 127 tests in 24.527s, OK. | PASS |
```

Use this table shape for package tests, targeted init tests, dry-run command from `/Users/huangchihan/develop/bbj/peasydeal/peasydeal_be`, and target git status before/after.

**Phase 5 validation inputs** (`05-VALIDATION.md` lines 46-47):

```markdown
| 05-02-01 | 02 | 2 | TEST-07 | T-05-06 | `peasydeal_be` validation remains dry-run only and target git status is unchanged before and after. | smoke/report | `python3 skills/project-llm-wiki/scripts/project_wiki.py init --dry-run` from `/Users/huangchihan/develop/bbj/peasydeal/peasydeal_be` | No - report W0 | pending |
| 05-03-01 | 03 | 3 | TEST-07 | T-05-07 | Rollout report gives PASS / FLAG / BLOCK with evidence from package tests and `peasydeal_be` dry-run. | doc/report | `python3 -m unittest discover -s skills/project-llm-wiki/tests` | No - report W0 | pending |
```

The report must include resolved git root, would-create/would-update paths, managed root `AGENTS.md` section, conflict status, and unchanged target repo status. Do not write to `peasydeal_be`.

**Roadmap success criteria** (`ROADMAP.md` lines 101-106):

```markdown
**Success Criteria** (what must be TRUE):
  1. User can insert a Project LLM Wiki section into repo `AGENTS.md` without overwriting unrelated guidance.
  2. Existing NotebookLM and workflow sections remain unchanged in fixture tests.
  3. Inserted rules tell agents when to read `.llm-wiki/index.md`, when to update `.llm-wiki/`, and that repo code wins over wiki notes.
  4. `peasydeal_be` dry-run validation reports expected changes without destructive edits.
  5. The final rollout report identifies whether the pattern is ready for `peasydeal_web` and `peasydeal-product-miner`.
```

Use these criteria as report sections or a final checklist.

## Shared Patterns

### Python Standard Library Only

**Source:** `project_wiki.py` lines 2-9 and `test_project_wiki_package.py` lines 207-230

Apply to: `project_wiki.py`, all tests.

Keep implementation and tests on stdlib modules. Package tests enforce imported modules, so any import change must be intentional and reflected there.

### Git Root Is the Write Boundary

**Source:** `project_wiki.py` lines 149-160 and `test_project_wiki_init.py` lines 52-84

Apply to: `project_wiki.py`, init tests, rollout report.

All generated paths are relative to the Git root resolved by `git rev-parse --show-toplevel`. Root `AGENTS.md` is `git_root / "AGENTS.md"`.

### Pure Plan Before Apply

**Source:** `project_wiki.py` lines 1503-1556

Apply to: `project_wiki.py`, init tests, rollout report.

Build skeleton and AGENTS patch plans before any writes. Dry-run and apply must consume the same plan. Conflicts return `2` before partial writes.

### Dry-Run Prints Evidence Without Writes

**Source:** `project_wiki.py` lines 1522-1540 and `test_project_wiki_init.py` lines 102-117

Apply to: `project_wiki.py`, init tests, rollout report.

Dry-run currently prints `Would create paths:`, `Would skip existing paths:`, source status, conflicts, and next step. Phase 5 should add AGENTS action and the exact managed section while preserving no-write behavior.

### Marker-Bounded Root AGENTS Patch

**Source:** `05-CONTEXT.md` lines 31-36 and `05-RESEARCH.md` lines 203-215

Apply to: `project_wiki.py`, init tests, command docs, rollout report.

Use exact markers:

```text
<!-- PROJECT-LLM-WIKI:START -->
<!-- PROJECT-LLM-WIKI:END -->
```

Create root `AGENTS.md` when missing, append when no markers exist, replace only the inclusive marker-bounded section when exactly one valid pair exists, and treat invalid UTF-8, unmatched markers, or multiple marker pairs as conflicts.

### Marker-External Byte Preservation

**Source:** `05-RESEARCH.md` lines 328-331 and `peasydeal_be/AGENTS.md` lines 30-44

Apply to: `project_wiki.py`, init tests, rollout report.

Test with `read_bytes()`, not normalized text. Preserve NotebookLM, GSD, workflow, and repo-specific sections outside the managed Project LLM Wiki markers.

### Docs Locked by Package Tests

**Source:** `test_project_wiki_package.py` lines 123-183

Apply to: `command-surface.md`, `testing.md`, optional `SKILL.md`.

When docs move AGENTS integration out of deferred status, add package assertions in the same commit/plan so future drift is visible in the normal test suite.

### Report Verdict Uses PASS / FLAG / BLOCK

**Source:** `05-CONTEXT.md` lines 40-42 and `05-VALIDATION.md` lines 46-47

Apply to: `05-ROLLOUT-REPORT.md`.

`PASS` requires fixtures, package tests, and `peasydeal_be` dry-run to pass. `FLAG` means usable with manual confirmation items. `BLOCK` means conflicts, preservation risk, or test failure.

## No Analog Found

| File / Subpattern | Role | Data Flow | Reason |
|-------------------|------|-----------|--------|
| Root `AGENTS.md` marker-bounded byte replacement helper inside `project_wiki.py` | utility helper | file-I/O transform | No existing helper patches root `AGENTS.md` markers. Use the Phase 5 research pattern and existing init conflict/dry-run/apply scaffolding. |
| `peasydeal_be` dry-run rollout report content | report | smoke / external-repo dry-run | Prior reports verify in-repo behavior, but no existing report records dry-run evidence against another repo. Use `04-VERIFICATION.md` table structure plus Phase 5 validation requirements. |

## Metadata

**Analog search scope:** `skills/project-llm-wiki/`, `.planning/phases/05-agent-instructions-and-real-repo-validation/`, prior phase verification/summary artifacts, and read-only fixture source `/Users/huangchihan/develop/bbj/peasydeal/peasydeal_be/AGENTS.md`.

**Files scanned:** 18 direct files plus repo-wide `rg` lookups for rollout/report patterns.

**Project instructions loaded:** `AGENTS.md`; project-local `.codex/skills/` and `.agents/skills/` were absent; `skills/project-llm-wiki/SKILL.md` was loaded as the local skill index.

**Pattern extraction date:** 2026-05-14
