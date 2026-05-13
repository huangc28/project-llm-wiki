# Phase 3: Lint and Safety Checks - Pattern Map

**Mapped:** 2026-05-13
**Files analyzed:** 5 new/modified targets
**Analogs found:** 5 / 5

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `skills/project-llm-wiki/scripts/project_wiki.py` | utility / CLI | request-response, file-I/O, transform | `skills/project-llm-wiki/scripts/project_wiki.py` | exact surface, new lint behavior |
| `skills/project-llm-wiki/tests/test_project_wiki_lint.py` | test | request-response, file-I/O | `skills/project-llm-wiki/tests/test_project_wiki_init.py` | role-match |
| `skills/project-llm-wiki/tests/test_project_wiki_package.py` | test | transform, static validation | `skills/project-llm-wiki/tests/test_project_wiki_package.py` | exact |
| `skills/project-llm-wiki/references/command-surface.md` | config / reference docs | static content | `skills/project-llm-wiki/references/command-surface.md` | exact |
| `skills/project-llm-wiki/references/testing.md` | config / reference docs | static content | `skills/project-llm-wiki/references/testing.md` | exact |

## Pattern Assignments

### `skills/project-llm-wiki/scripts/project_wiki.py` (utility / CLI, request-response + file-I/O + transform)

**Analog:** `skills/project-llm-wiki/scripts/project_wiki.py`

**Imports pattern** (lines 1-6):

```python
#!/usr/bin/env python3
import argparse
import pathlib
import subprocess
import sys
import textwrap
```

Keep lint stdlib-only. Phase 3 may add only stdlib modules that lint actually uses, such as `datetime`, `json`, or `re`, and the package whitelist test must track the exact imports.

**Path constants pattern** (lines 9-42):

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
RECOMMENDED_INDEX_LINKS = ("[[features/ideas]]", "[[summaries/repo-overview]]")
```

Reuse `WIKI_ROOT` and existing category constants where possible. For Phase 3 index coverage, extend this pattern into explicit lint inventory helpers rather than scattering string paths through checks.

**Git-root boundary pattern** (lines 62-73):

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

Lint should resolve the same git root before inspecting `.llm-wiki/`. Missing git root or missing wiki root is an operational CLI failure, not a partial filesystem scan from the current directory.

**Filesystem safety guard pattern** (lines 155-189):

```python
def path_is_under(path: pathlib.Path, root: pathlib.Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve())
    except ValueError:
        return False
    return True


def find_init_conflicts(git_root: pathlib.Path) -> list[str]:
    conflicts: list[str] = []
    for relative_path in REQUIRED_DIRECTORIES:
        path = git_root / relative_path
        if path.is_symlink():
            conflicts.append(
                f"{relative_path.as_posix()}: expected real directory, found symlink"
            )
```

Copy the conservative path posture for lint: do not follow `.llm-wiki/` symlink escapes outside the resolved repo, and report clear paths when a required wiki path is not safe to inspect.

**UTF-8 read and warning collection pattern** (lines 192-201):

```python
def collect_missing_index_links(git_root: pathlib.Path) -> tuple[list[str], str | None]:
    index_path = git_root / ".llm-wiki" / "index.md"
    if not index_path.is_file():
        return [], None

    try:
        index_text = index_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [], ".llm-wiki/index.md: expected UTF-8 markdown, could not read"
    return [link for link in RECOMMENDED_INDEX_LINKS if link not in index_text], None
```

Use explicit UTF-8 reads and convert unreadable wiki files into deterministic findings or operational errors. Do not let Unicode errors produce tracebacks.

**Human text rendering pattern** (lines 250-265):

```python
def print_path_section(heading: str, paths: list[pathlib.Path]) -> None:
    print(heading)
    if not paths:
        print("- (none)")
        return
    for path in paths:
        print(f"- {path.as_posix()}")


def print_text_section(heading: str, items: list[str]) -> None:
    print(heading)
    if not items:
        print("- (none)")
        return
```

Text lint output should stay simple and line-oriented. Render fixed finding fields in stable order; print `No issues found in .llm-wiki/` when the finding list is empty.

**Command handler pattern** (lines 273-332):

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
```

Implement `run_lint(args)` as the sibling to `run_init(args)`: resolve root, validate wiki presence/safety, collect findings, render text or JSON, and return `1` only if any finding has `severity == "error"`.

**Parser and subcommand pattern** (lines 335-376):

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
            lint, query, and ingest remain planned for later phases.
            """
        ),
    )
```

Replace only the `lint` planned-command stub with a real subparser handler. Add `lint.add_argument("--json", action="store_true", ...)`; leave `query` and `ingest` deferred.

**Main pattern** (lines 379-386):

```python
def main(argv: list[str] | None = None) -> int:
    _script_path = pathlib.Path(__file__)
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__": raise SystemExit(main())
```

Keep handlers returning process codes instead of calling `sys.exit()` internally.

---

### `skills/project-llm-wiki/tests/test_project_wiki_lint.py` (test, request-response + file-I/O)

**Analog:** `skills/project-llm-wiki/tests/test_project_wiki_init.py`

**Imports and constants pattern** (lines 1-10):

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

Copy this structure for the new lint test file. Add stdlib `json` only if the tests parse `lint --json` output.

**Subprocess helper pattern** (lines 13-41):

```python
class ProjectWikiInitTests(unittest.TestCase):
    def run_git(self, repo: Path, *args: str):
        return subprocess.run(
            ["git", *args],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )

    def init_repo(self, repo: Path):
        result = subprocess.run(
            ["git", "init"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        return result

    def run_helper(self, cwd: Path, *args: str):
        return subprocess.run(
            [sys.executable, str(HELPER), *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
```

Lint tests should run through the same CLI subprocess boundary. Build fixtures by running `init`, mutating `.llm-wiki/`, then invoking `lint` or `lint --json`.

**Generated skeleton fixture pattern** (lines 245-265):

```python
def test_clean_repo_status_shows_llm_wiki_files(self):
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        self.init_repo(repo)

        result = self.run_helper(repo, "init")
        output = result.stdout + result.stderr
        status = self.git_status_short(repo)

        self.assertEqual(0, result.returncode, output)
        self.assertEqual(0, status.returncode, status.stdout + status.stderr)
        self.assertTrue((repo / ".llm-wiki" / "README.md").exists())
        self.assertTrue((repo / ".llm-wiki" / "index.md").exists())
        self.assertTrue((repo / ".llm-wiki" / "raw" / "README.md").exists())
        self.assertTrue((repo / ".llm-wiki" / "raw" / "curated" / "README.md").exists())
        self.assertTrue((repo / ".llm-wiki" / "features" / "ideas.md").exists())
        self.assertTrue((repo / ".llm-wiki" / "summaries" / "repo-overview.md").exists())
```

Add a clean-skeleton lint test first: after `init`, `lint` exits `0` and reports no issues. This guards against noisy index, secret, raw-size, and stale checks.

**Existing missing-index behavior pattern** (lines 267-290):

```python
index = repo / ".llm-wiki" / "index.md"
overview = repo / ".llm-wiki" / "summaries" / "repo-overview.md"
index.write_text("# Custom Index\n\nSentinel\n", encoding="utf-8")
overview.write_text("# Custom Overview\n\nSentinel\n", encoding="utf-8")

rerun = self.run_helper(repo, "init")
output = rerun.stdout + rerun.stderr

self.assertEqual(0, rerun.returncode, output)
self.assertIn("Missing recommended index links:", output)
self.assertIn("[[features/ideas]]", output)
self.assertIn("[[summaries/repo-overview]]", output)
```

Use the same mutate-then-assert shape for `missing_index_entry` lint warnings, but assert fixed finding fields instead of init's recommended-link section.

**Raw policy fixture source** (lines 315-347):

```python
raw_readme = (repo / ".llm-wiki" / "raw" / "README.md").read_text(
    encoding="utf-8"
)
curated_readme = (
    repo / ".llm-wiki" / "raw" / "curated" / "README.md"
).read_text(encoding="utf-8")
ideas = (repo / ".llm-wiki" / "features" / "ideas.md").read_text(
    encoding="utf-8"
)

self.assertIn(
    "secrets, credentials, auth tokens, private customer data, full logs, database exports, generated dumps",
    raw_readme,
)
self.assertIn("de-secreted", curated_readme)
self.assertIn("Related links", ideas)
```

Use real template policy pages as controls. Secret-like detection must not trigger on policy prose alone; fixture secrets should use high-confidence shapes such as private key blocks or credential URLs.

---

### `skills/project-llm-wiki/tests/test_project_wiki_package.py` (test, transform + static validation)

**Analog:** `skills/project-llm-wiki/tests/test_project_wiki_package.py`

**Helper subprocess pattern** (lines 12-19):

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

Use this file for lightweight helper surface checks only. Put lint behavior fixtures in `test_project_wiki_lint.py`.

**Help and version smoke pattern** (lines 39-49):

```python
def test_helper_help_exits_zero(self):
    result = self.run_helper("--help")

    self.assertEqual(0, result.returncode)
    self.assertIn("Repo-local .llm-wiki helper for Project LLM Wiki", result.stdout)

def test_helper_version_output(self):
    result = self.run_helper("version")

    self.assertEqual(0, result.returncode)
    self.assertIn("project-llm-wiki 0.1.0-foundation", result.stdout)
```

Add a small `lint --help` assertion here only if needed to prove `--json` is on the command surface.

**Import whitelist pattern** (lines 67-81):

```python
def test_helper_imports_only_allowed_modules(self):
    allowed = {"argparse", "pathlib", "subprocess", "sys", "textwrap"}
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

Update `allowed` only for modules actually imported by lint. Expected additions from research are `datetime`, `json`, and `re`; do not add unused modules preemptively.

---

### `skills/project-llm-wiki/references/command-surface.md` (config / reference docs, static content)

**Analog:** `skills/project-llm-wiki/references/command-surface.md`

**Current lint boundary wording** (lines 15-18):

```markdown
### project-wiki-lint

Planned mode for checking broken wikilinks, missing index entries, secret-looking content, oversized raw files, stale pages, and likely repo/wiki contradictions.
```

Update this from planned-mode language to the Phase 3 concrete behavior once lint is implemented. Include `project-wiki lint --json`, warning-only exit `0`, and error exit `1`.

**Deferred behavior section** (lines 43-50):

```markdown
## Deferred Behavior

Full command behavior is deferred to later phases:

- Init and wiki templates: Phase 2
- Lint and safety checks: Phase 3
- Query and ingest loop: Phase 4
- AGENTS integration and real repo validation: Phase 5
```

If this file is updated in Phase 3, remove lint from deferred behavior while keeping query/ingest/promotion deferred.

---

### `skills/project-llm-wiki/references/testing.md` (config / reference docs, static content)

**Analog:** `skills/project-llm-wiki/references/testing.md`

**Test command pattern** (lines 3-8):

```markdown
## Test Command

Run package tests with:

`python3 -m unittest discover -s skills/project-llm-wiki/tests`
```

Preserve this full-suite command. Add a Phase 3 quick command for `test_project_wiki_lint.py` only if the planner wants a targeted red/green loop.

**Validation contract style** (lines 9-24):

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
```

Mirror this structure for Phase 3 lint: state the subprocess boundary, temporary Git repo fixtures, clean-skeleton control, broken wikilink errors, warning-only checks, JSON output, and fixed fields.

**No dependency rule** (lines 35-41):

```markdown
## No Dependency Rule

The helper script should stay on the Python standard library. The import
whitelist test must be updated only when `project_wiki.py` actually imports a new
standard-library module.

Tests should use Python standard-library modules only.
```

Keep this exact constraint active for lint and tests.

## Shared Patterns

### Standard-Library-Only Runtime

**Source:** `skills/project-llm-wiki/scripts/project_wiki.py` lines 1-6, `skills/project-llm-wiki/references/testing.md` lines 35-41

```markdown
The helper script should stay on the Python standard library. The import
whitelist test must be updated only when `project_wiki.py` actually imports a new
standard-library module.
```

Apply to `project_wiki.py`, lint tests, and package tests. No third-party Markdown, YAML, or secret-scanning dependency belongs in Phase 3.

### Repo Boundary and Symlink Safety

**Source:** `skills/project-llm-wiki/scripts/project_wiki.py` lines 62-73 and 155-189

```python
result = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"],
    cwd=cwd,
    capture_output=True,
    text=True,
    check=False,
)
```

Lint should inspect `.llm-wiki/` under the resolved git root only. Required wiki roots should be real paths under the repo, not symlink escapes.

### Fixed Finding Contract

**Source:** `.planning/phases/03-lint-and-safety-checks/03-CONTEXT.md` decisions D-20 through D-26

```markdown
Every finding uses fixed fields: `severity`, `code`, `path`, `message`, and `remediation`. JSON output uses the same fields.
```

Use one internal finding representation for all checks, then render text and JSON from it. Severity names are exactly `error` and `warning`.

### Read-Only Lint

**Source:** `.planning/phases/03-lint-and-safety-checks/03-CONTEXT.md` decisions D-16 and D-26

```markdown
Lint must not update `updated:` automatically.
Phase 3 lint does not modify files. It only reports findings and remediation guidance.
```

All lint helpers should collect and report. They must not write wiki files, update dates, repair links, or edit `index.md`.

### Obsidian Wikilinks

**Source:** `skills/project-llm-wiki/assets/templates/llm-wiki/index.md` lines 5-6 and 32-34

```markdown
- Summary seed: [[summaries/repo-overview]]
- Durable ideas: [[features/ideas]]

Use `raw/curated/` only for small, de-secreted, intentionally selected sources or excerpts. See [[raw/README]] and [[raw/curated/README]] before adding material.
```

Normalize `[[path]]`, `[[path.md]]`, `[[path|Alias]]`, and `[[path#Heading]]` consistently. Alias text and heading fragments are ignored for Phase 3 existence checks.

### Raw Safety Policy

**Source:** `skills/project-llm-wiki/assets/templates/llm-wiki/raw/README.md` lines 11-20 and `raw/curated/README.md` lines 1-9

```markdown
Do not store secrets, credentials, auth tokens, private customer data, full logs, database exports, generated dumps, or other unsafe material in `.llm-wiki/raw/`.
```

Secret-looking detection must be high-confidence enough that the default policy pages do not warn on their own wording.

### Test Boundary

**Source:** `skills/project-llm-wiki/tests/test_project_wiki_init.py` lines 34-41

```python
return subprocess.run(
    [sys.executable, str(HELPER), *args],
    cwd=cwd,
    capture_output=True,
    text=True,
    check=False,
)
```

Behavior tests should exercise the CLI as users and agents will run it, not call private helpers directly.

## No Analog Found

| File / Behavior | Role | Data Flow | Reason |
|-----------------|------|-----------|--------|
| Wikilink normalization helpers in `project_wiki.py` | utility | transform | No existing parser normalizes Obsidian aliases/headings/extensions; implement from Phase 3 decisions D-01 through D-04. |
| Lint finding model and JSON renderer in `project_wiki.py` | utility | transform, request-response | Current CLI has text sections only and no JSON output; use fixed field contract from D-20 through D-26. |
| Stale frontmatter date check in `project_wiki.py` | utility | transform | No current frontmatter reader exists; implement minimal `updated: YYYY-MM-DD` top-block parsing only. |
| Repo path drift extraction in `project_wiki.py` | utility | transform, file-I/O | No existing code-span/fenced-block scanner exists; scan only Markdown code spans and fenced code blocks per D-17 through D-19. |
| Oversized raw file warning in `project_wiki.py` | utility | file-I/O | Existing init writes raw policy files but does not inspect file sizes; limit warning checks to `.llm-wiki/raw/` over 100 KB. |

## Metadata

**Analog search scope:** `skills/project-llm-wiki/`, `.planning/phases/02-init-and-wiki-templates/02-PATTERNS.md`, `.planning/phases/03-lint-and-safety-checks/03-CONTEXT.md`, `.planning/phases/03-lint-and-safety-checks/03-RESEARCH.md`, root `AGENTS.md`

**Files scanned:** 12 package/source/planning files

**Strong analogs used:** 7 (`project_wiki.py`, `test_project_wiki_init.py`, `test_project_wiki_package.py`, `command-surface.md`, `testing.md`, `index.md`, `raw/README.md`)

**Pattern extraction date:** 2026-05-13
