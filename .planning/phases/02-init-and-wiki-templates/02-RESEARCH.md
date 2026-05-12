# Phase 2: Init and Wiki Templates - Research

**Researched:** 2026-05-13
**Domain:** Python standard-library CLI initialization, Git root detection, Markdown wiki template generation
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

All constraints in this section are copied from `.planning/phases/02-init-and-wiki-templates/02-CONTEXT.md`. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]

### Locked Decisions

## Implementation Decisions

### Git-root and Safety Behavior
- **D-01:** `project-wiki-init` must resolve the actual repository root with `git rev-parse --show-toplevel`; when run from a subdirectory, it creates `.llm-wiki/` at the resolved git root, not the current directory.
- **D-02:** If init is run from a multi-repo parent or another non-target workspace, it must not write. It may list candidate child git repos when discoverable, then tell the user to `cd` into the intended repo before running init.
- **D-03:** Phase 2 does not support `--target`. Explicit target selection is deferred; this phase only initializes the current actual repo.
- **D-04:** Successful and failed output should be concise: resolved git root, created paths, skipped paths, conflicts when present, and the next useful command.
- **D-05:** Shared FE/BE knowledge is not represented by writing `.llm-wiki/` into a workspace parent. Each code repo keeps its own `.llm-wiki/`; shared cross-repo context belongs in a dedicated shared repo such as `peasydeal-context/.llm-wiki/`.

### Template Skeleton Shape
- **D-06:** The initial skeleton should be minimal but complete: required landing pages plus the planned category directories, without excessive starter content.
- **D-07:** Create these initial files and directories: `README.md`, `AGENTS.md`, `index.md`, `log.md`, `raw/README.md`, `raw/curated/README.md`, `architecture/`, `domain/`, `decisions/`, `operations/`, `features/`, `summaries/`, and `raw/curated/`.
- **D-08:** Add `.gitkeep` to otherwise-empty category directories so the complete skeleton appears in `git status`.
- **D-09:** Add `.llm-wiki/features/ideas.md` and link it from `index.md`. This page is for durable but immature ideas; it is not a roadmap, backlog, or active task-state store.
- **D-10:** Initial pages should be short guidance templates: purpose, what belongs there, what does not belong there, and a few example links.
- **D-11:** The skeleton is a stable default, not a permanent schema. Future structure changes should be additive or migration-based and must not overwrite existing notes.

### Seeding From Existing Repo Files
- **D-12:** Seed with light summary plus provenance only. Do not attempt deep interpretation during init.
- **D-13:** Phase 2 may read only `README.md` and `AGENTS.md` for seed content. These are human-authored orientation/instruction files.
- **D-14:** Do not seed wiki content from language manifests or config files such as `package.json`, `pyproject.toml`, `go.mod`, or `Cargo.toml`. Future agents should read current repo files directly when they need tech-stack facts.
- **D-15:** Write seeded content to `.llm-wiki/summaries/repo-overview.md` and link it from `index.md`.
- **D-16:** If `README.md` or `AGENTS.md` is missing, init should still create the skeleton and report the source as skipped.

### Idempotency and Existing-file Policy
- **D-17:** Re-running init must never overwrite existing files. It only creates missing files/directories and reports skipped paths.
- **D-18:** If an existing `.llm-wiki/index.md` is missing links to new default pages, init must not edit it. It should report missing links in output so the user can update manually.
- **D-19:** If a required directory path is occupied by a file, init must fail before partial writes and list each conflict with the expected path type.
- **D-20:** Support `--dry-run`; it reports would-create, would-skip, and conflicts without writing files.

### Raw Source Policy
- **D-21:** `.llm-wiki/raw/README.md` should use a strict allow/deny policy.
- **D-22:** Raw policy must explicitly forbid secrets, credentials, auth tokens, private customer data, full logs, database exports, generated dumps, and other unsafe material.
- **D-23:** Create `.llm-wiki/raw/curated/README.md` explaining that curated raw sources must be de-secreted, intentionally selected, and small sources or excerpts.
- **D-24:** Init does not perform secret scanning. Deterministic secret and safety checks belong to Phase 3 lint.
- **D-25:** Use a light naming convention for curated raw files, such as date or source-name based filenames (`2026-05-13-api-notes.md`), but do not enforce naming in Phase 2.

### the agent's Discretion
The planner may decide exact function boundaries, test fixture names, template wording, and output formatting details as long as the decisions above remain true and the implementation stays standard-library only.

### Deferred Ideas (OUT OF SCOPE)

## Deferred Ideas

- Support explicit cross-repo querying across repo-local wikis and a dedicated shared wiki after the single-repo workflow is proven.
- Support explicit target selection such as `--target path/to/repo` in a later phase if the parent-workspace workflow proves necessary.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| INIT-01 | Initialize `.llm-wiki/` in the actual git root detected by `git rev-parse --show-toplevel`. [VERIFIED: .planning/REQUIREMENTS.md] | Use `subprocess.run(["git", "rev-parse", "--show-toplevel"], shell=False)` and write only under the returned root. [CITED: https://git-scm.com/docs/git-rev-parse] |
| INIT-02 | Give a clear failure or target-selection message outside a git repo or from a multi-repo parent. [VERIFIED: .planning/REQUIREMENTS.md] | Treat nonzero `rev-parse` as no target repo; for discoverable child repos, report candidates and do not write. [CITED: https://git-scm.com/docs/git-rev-parse] |
| INIT-03 | Create the required `.llm-wiki/` skeleton. [VERIFIED: .planning/REQUIREMENTS.md] | Store skeleton Markdown assets in `skills/project-llm-wiki/assets/templates/` and create empty category directories plus `.gitkeep`. [VERIFIED: skills/project-llm-wiki/assets/templates/README.md] |
| INIT-04 | Rerun init without overwriting notes or duplicating generated sections. [VERIFIED: .planning/REQUIREMENTS.md] | Build a preflight plan, create missing paths only, and never edit existing wiki files. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md] |
| INIT-05 | Seed concise starting pages from existing repo files. [VERIFIED: .planning/REQUIREMENTS.md] | Phase context narrows this to `README.md` and `AGENTS.md` only, explicitly excluding package manifests and language config files. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md] |
| INIT-06 | Show `.llm-wiki/` files in `git status` after init unless already ignored. [VERIFIED: .planning/REQUIREMENTS.md] | Add real files and `.gitkeep` placeholders so Git has untracked paths to report. [CITED: https://git-scm.com/docs/git-status] |
| RAW-01 | Explain allowed and disallowed raw sources in `.llm-wiki/raw/README.md`. [VERIFIED: .planning/REQUIREMENTS.md] | Add raw policy template content under `assets/templates/llm-wiki/raw/README.md`. [VERIFIED: skills/project-llm-wiki/assets/templates/README.md] |
| RAW-02 | Warn against secrets, credentials, private customer data, tokens, full logs, DB exports, and dumps. [VERIFIED: .planning/REQUIREMENTS.md] | Put the warning in both raw policy templates; do not claim deterministic enforcement until Phase 3. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md] |
| RAW-03 | Allow only curated, de-secreted project sources under `.llm-wiki/raw/curated/`. [VERIFIED: .planning/REQUIREMENTS.md] | Create `raw/curated/README.md` as a strict usage contract. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md] |
| TEST-01 | A clean test repo can run init and show `.llm-wiki/` files in `git status`. [VERIFIED: .planning/REQUIREMENTS.md] | Use `tempfile.TemporaryDirectory`, `git init`, helper subprocess execution, and `git status --short`. [CITED: https://docs.python.org/3/library/tempfile.html] |
| TEST-02 | A clean test repo can rerun init without duplicated sections or overwritten notes. [VERIFIED: .planning/REQUIREMENTS.md] | Add a sentinel-content fixture, rerun init, and assert existing content is unchanged. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py] |
</phase_requirements>

## Project Constraints (from AGENTS.md)

- Work is already inside a GSD phase workflow; file-changing work should stay synchronized with GSD planning artifacts. [VERIFIED: AGENTS.md]
- Keep edits small, reviewable, and reversible; Phase 2 plans should modify only package-owned files unless a plan explicitly widens scope. [VERIFIED: AGENTS.md; VERIFIED: skills/project-llm-wiki/references/package-contract.md]
- Prefer Markdown templates plus small scripts and avoid new dependencies unless clearly necessary. [VERIFIED: AGENTS.md]
- Verify with the package test command after changes: `python3 -m unittest discover -s skills/project-llm-wiki/tests`. [VERIFIED: skills/project-llm-wiki/SKILL.md; VERIFIED: skills/project-llm-wiki/references/testing.md]
- If research docs are committed, commit messages must follow the Lore Commit Protocol trailers. [VERIFIED: AGENTS.md]
- Do not revert unrelated work; current `git status --short` shows `AGENTS.md` is already modified and must be left alone by Phase 2 research. [VERIFIED: git status --short]
- No project-local `.codex/skills/` or `.agents/skills/` skill files were found during discovery. [VERIFIED: find .codex/skills .agents/skills -maxdepth 2 -name SKILL.md]

## Summary

Phase 2 should replace the existing planned `init` stub in `skills/project-llm-wiki/scripts/project_wiki.py` with deterministic initialization behavior and should keep all template assets under `skills/project-llm-wiki/assets/templates/`. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py; VERIFIED: skills/project-llm-wiki/assets/templates/README.md] The implementation should remain Python standard-library only, using the current `argparse` command surface, `subprocess.run` for Git, `pathlib.Path` for filesystem operations, and `unittest` plus temporary Git repositories for validation. [CITED: https://docs.python.org/3/library/argparse.html; CITED: https://docs.python.org/3/library/subprocess.html; CITED: https://docs.python.org/3/library/pathlib.html; CITED: https://docs.python.org/3/library/unittest.html]

The highest-risk planning issue is idempotency. `pathlib.Path.write_text()` overwrites an existing file, so implementation must preflight all required paths, detect file-vs-directory conflicts before any writes, and guard every create operation so reruns only report skipped files. [CITED: https://docs.python.org/3/library/pathlib.html] The second planning issue is the INIT-05 scope mismatch: the project requirements mention package manifests, but Phase 2 context explicitly locks seeding to `README.md` and `AGENTS.md` only. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]

**Primary recommendation:** Plan a three-slice implementation: first git-root resolution, dry-run, and no-partial-write safety; second static template assets and README/AGENTS seed generation; third clean temporary Git repo tests for status visibility and rerun idempotency. [VERIFIED: .planning/ROADMAP.md; VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| Git root detection | CLI helper process | Git CLI | `git rev-parse --show-toplevel` is the authoritative Git worktree root mechanism for this phase. [CITED: https://git-scm.com/docs/git-rev-parse] |
| Non-repo and parent-workspace safety | CLI helper process | Filesystem discovery | The helper owns refusing writes and may list child repo candidates when discoverable. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md] |
| `.llm-wiki/` skeleton generation | CLI helper process | Package template assets | The package owns templates and init behavior under `skills/project-llm-wiki/`. [VERIFIED: skills/project-llm-wiki/assets/templates/README.md] |
| Existing-file idempotency | CLI helper process | Filesystem | Existing wiki files must be skipped and never overwritten. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md] |
| README/AGENTS seeding | CLI helper process | Target repo files | Init reads only target repo `README.md` and `AGENTS.md` and writes a light provenance page if missing. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md] |
| Raw source policy | Markdown templates | Future lint phase | Phase 2 writes policy text; Phase 3 owns deterministic secret and safety checks. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md] |
| Validation fixtures | Test suite | Git CLI | Clean repo and rerun behavior should be tested through subprocess execution in temporary Git repositories. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py; CITED: https://docs.python.org/3/library/tempfile.html] |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python standard library | Local `python3` is 3.14.3; official docs checked at 3.14.5. [VERIFIED: python3 --version; CITED: https://docs.python.org/3/] | Implement CLI parsing, subprocess Git calls, path operations, and text file creation. [CITED: https://docs.python.org/3/library/] | Project already requires standard-library-only implementation for v1. [VERIFIED: .planning/PROJECT.md; VERIFIED: skills/project-llm-wiki/references/testing.md] |
| `argparse` | Python stdlib. [CITED: https://docs.python.org/3/library/argparse.html] | Keep and extend the existing subcommand parser with `init --dry-run`. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py] | It automatically supports user-friendly CLI parsing and help text without third-party dependencies. [CITED: https://docs.python.org/3/library/argparse.html] |
| `subprocess` | Python stdlib. [CITED: https://docs.python.org/3/library/subprocess.html] | Invoke `git rev-parse`, `git init`, and `git status` in implementation/tests. [CITED: https://git-scm.com/docs/git-rev-parse; CITED: https://git-scm.com/docs/git-status] | Python docs recommend `subprocess.run()` for use cases it can handle. [CITED: https://docs.python.org/3/library/subprocess.html] |
| `pathlib` | Python stdlib. [CITED: https://docs.python.org/3/library/pathlib.html] | Build and inspect target paths, create directories, and read/write template files. [CITED: https://docs.python.org/3/library/pathlib.html] | Existing code and tests already use `pathlib`. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py; VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py] |
| Git CLI | Local Git is 2.50.1. [VERIFIED: git --version] | Resolve root and validate untracked wiki visibility. [CITED: https://git-scm.com/docs/git-rev-parse; CITED: https://git-scm.com/docs/git-status] | Requirements lock `git rev-parse --show-toplevel` as the root detector. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md] |
| Markdown template assets | Repo-local package files. [VERIFIED: skills/project-llm-wiki/assets/templates/README.md] | Store initial `.llm-wiki/` pages and raw policy text. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md] | Templates are inspectable and keep prompt bulk out of `SKILL.md`. [VERIFIED: .planning/phases/01-skill-package-foundation/01-RESEARCH.md] |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `tempfile.TemporaryDirectory` | Python stdlib. [CITED: https://docs.python.org/3/library/tempfile.html] | Create clean disposable Git repos for tests. [CITED: https://docs.python.org/3/library/tempfile.html] | Use in TEST-01 and TEST-02 fixtures. [VERIFIED: .planning/REQUIREMENTS.md] |
| `unittest` | Python stdlib. [CITED: https://docs.python.org/3/library/unittest.html] | Extend current package test suite. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py] | Use because current tests and project testing reference already use it. [VERIFIED: skills/project-llm-wiki/references/testing.md] |
| `textwrap` | Python stdlib. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py] | Keep help text and generated template snippets readable. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py] | Continue only where it improves static text formatting. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py] |
| `rg` | Local ripgrep is 15.1.0. [VERIFIED: rg --version] | Developer inspection only. [VERIFIED: rg --version] | Do not make runtime behavior depend on `rg`; the package contract is stdlib plus Git. [VERIFIED: .planning/PROJECT.md] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `argparse` | Click or Typer | Reject for Phase 2 because the project has a no-new-dependency rule and the current parser already uses `argparse`. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py; VERIFIED: .planning/PROJECT.md] |
| Static Markdown assets | Jinja2 templates | Reject for Phase 2 because dynamic templating needs are limited to seed/provenance text and Jinja2 would add a dependency. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md; VERIFIED: .planning/PROJECT.md] |
| `git rev-parse --show-toplevel` | Manual parent walking for `.git` | Reject because the phase explicitly requires `git rev-parse --show-toplevel` and Git docs define it as the top-level worktree path. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md; CITED: https://git-scm.com/docs/git-rev-parse] |
| Python helper | Shell-only script | Reject because existing package behavior, tests, and no-dependency contract are already Python stdlib based. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py; VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py] |

**Installation:**

No package installation is required for Phase 2. [VERIFIED: .planning/PROJECT.md]

```bash
python3 -m unittest discover -s skills/project-llm-wiki/tests
```

**Version verification:** No npm packages are recommended. Local tool versions verified: `python3` 3.14.3, Git 2.50.1, ripgrep 15.1.0. [VERIFIED: python3 --version; VERIFIED: git --version; VERIFIED: rg --version]

## Architecture Patterns

### System Architecture Diagram

```text
User cwd
  |
  v
project_wiki.py init [--dry-run]
  |
  v
git rev-parse --show-toplevel
  |-- nonzero/no worktree --> discover optional child repos --> print failure, no writes
  |
  v
resolved git root
  |
  v
build init plan
  |-- expected directories
  |-- expected template files
  |-- README.md / AGENTS.md seed source status
  |
  v
preflight all paths
  |-- file blocks required directory --> print conflicts, no writes
  |-- directory blocks required file --> print conflicts, no writes
  |
  v
dry-run?
  |-- yes --> print would-create / would-skip / skipped sources, no writes
  |
  v
apply missing-only plan
  |-- mkdir missing dirs
  |-- create missing files only
  |-- preserve existing wiki files
  |
  v
print root, created paths, skipped paths, skipped sources, next command
```

This architecture follows the locked decision that init writes only at the Git root returned by `git rev-parse --show-toplevel`. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md; CITED: https://git-scm.com/docs/git-rev-parse]

### Recommended Project Structure

```text
skills/project-llm-wiki/
├── SKILL.md
├── assets/
│   └── templates/
│       └── llm-wiki/
│           ├── README.md
│           ├── AGENTS.md
│           ├── index.md
│           ├── log.md
│           ├── raw/
│           │   ├── README.md
│           │   └── curated/
│           │       └── README.md
│           └── features/
│               └── ideas.md
├── references/
│   ├── command-surface.md
│   ├── package-contract.md
│   └── testing.md
├── scripts/
│   └── project_wiki.py
└── tests/
    └── test_project_wiki_package.py
```

The target repo output should be `.llm-wiki/` at the resolved Git root, not inside `skills/project-llm-wiki/assets/templates/`. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]

### Component Responsibilities

| Component | Responsibility | Planner Notes |
|-----------|----------------|---------------|
| `project_wiki.py` | CLI parser, Git root detection, dry-run, preflight, missing-only file creation, output. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py] | Replace `planned_command("project-wiki-init", "Phase 2")` with a real handler. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py] |
| `assets/templates/llm-wiki/` | Static default pages and raw policy text. [VERIFIED: skills/project-llm-wiki/assets/templates/README.md] | Add files here so templates stay inspectable and package-owned. [VERIFIED: skills/project-llm-wiki/assets/templates/README.md] |
| `summaries/repo-overview.md` generation | Light provenance summary from README/AGENTS. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md] | Generate from code because source existence varies per target repo. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md] |
| Test suite | Subprocess behavior, fixture Git repos, idempotency, raw policy content. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py] | Existing import whitelist must be updated if `subprocess` becomes a runtime import. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py] |

### Pattern 1: Git Root Resolution

**What:** Use Git as the source of truth for repository root detection. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]

**When to use:** Always at the start of `init`, before planning any target path. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]

**Example:**

```python
# Source: https://docs.python.org/3/library/subprocess.html
# Source: https://git-scm.com/docs/git-rev-parse
def resolve_git_root(cwd: Path) -> tuple[Path | None, str | None]:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None, result.stderr.strip() or "not inside a Git worktree"
    return Path(result.stdout.strip()), None
```

### Pattern 2: Preflight Before Writes

**What:** Construct the complete list of required directories and files, then detect all type conflicts before creating anything. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]

**When to use:** Before normal init and before dry-run reporting. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]

**Example:**

```python
# Source: https://docs.python.org/3/library/pathlib.html
def find_conflicts(root: Path, required_dirs: list[Path], required_files: list[Path]) -> list[str]:
    conflicts: list[str] = []
    for relative in required_dirs:
        path = root / relative
        if path.exists() and not path.is_dir():
            conflicts.append(f"{relative}: expected directory, found file")
    for relative in required_files:
        path = root / relative
        if path.exists() and not path.is_file():
            conflicts.append(f"{relative}: expected file, found directory")
    return conflicts
```

### Pattern 3: Create Missing Files Only

**What:** Write files only when absent; report existing files as skipped. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]

**When to use:** Every file creation path, including templates and generated `summaries/repo-overview.md`. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]

**Example:**

```python
# Source: https://docs.python.org/3/library/pathlib.html
def create_file_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True
```

Planner note: `Path.write_text()` overwrites an existing file, so the existence check is not optional. [CITED: https://docs.python.org/3/library/pathlib.html]

### Pattern 4: Clean Git Repo Fixture

**What:** Use a temporary directory, run `git init`, then execute the helper from inside that repo. [CITED: https://docs.python.org/3/library/tempfile.html; CITED: https://git-scm.com/docs/git-init]

**When to use:** TEST-01, TEST-02, non-root subdirectory tests, and dry-run tests. [VERIFIED: .planning/REQUIREMENTS.md]

**Example:**

```python
# Source: https://docs.python.org/3/library/tempfile.html
# Source: https://docs.python.org/3/library/subprocess.html
with tempfile.TemporaryDirectory() as tmp:
    repo = Path(tmp)
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    result = subprocess.run(
        [sys.executable, str(PACKAGE / "scripts" / "project_wiki.py"), "init"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
```

### Anti-Patterns to Avoid

- **Manual `.git` parent walking for root detection:** It can mis-handle worktrees, submodules, gitfiles, or Git environment settings; use `git rev-parse --show-toplevel`. [CITED: https://git-scm.com/docs/git-rev-parse]
- **Calling `Path.write_text()` on existing wiki files:** It overwrites existing content, which violates INIT-04 and D-17. [CITED: https://docs.python.org/3/library/pathlib.html; VERIFIED: .planning/REQUIREMENTS.md]
- **Writing incrementally before conflict detection:** D-19 requires failure before partial writes when required path types conflict. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]
- **Seeding from manifests in Phase 2:** D-14 explicitly excludes package manifests and language config from seed sources. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]
- **Turning raw policy into enforcement:** D-24 defers deterministic secret scanning to Phase 3. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Git root detection | Custom upward directory walk looking for `.git` | `git rev-parse --show-toplevel` | Git docs define this option as the top-level working tree path and the phase locks it. [CITED: https://git-scm.com/docs/git-rev-parse; VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md] |
| CLI parsing | Custom argument parsing | `argparse` | Existing helper already uses `argparse`, and Python docs describe it as the stdlib parser for command-line interfaces. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py; CITED: https://docs.python.org/3/library/argparse.html] |
| Template rendering | General-purpose templating engine | Static Markdown files plus one small generated seed page | Phase 2 templates are short guidance pages and the project forbids new dependencies unless necessary. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md; VERIFIED: .planning/PROJECT.md] |
| Secret detection | Regex scanner during init | Raw policy text now; Phase 3 lint later | D-24 explicitly defers deterministic secret checks. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md] |
| Git status internals | Parsing `.git/index` or object files | `git status --short` in tests | Git status has a documented short porcelain output for untracked files. [CITED: https://git-scm.com/docs/git-status] |

**Key insight:** Phase 2 is a filesystem initializer, not a knowledge interpreter. The planner should bias toward deterministic path planning, static templates, and explicit output over clever analysis. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]

## Common Pitfalls

### Pitfall 1: Existing Wiki Files Get Overwritten

**What goes wrong:** A rerun replaces user-edited `.llm-wiki/index.md`, `README.md`, or `summaries/repo-overview.md`. [VERIFIED: .planning/REQUIREMENTS.md]

**Why it happens:** `Path.write_text()` overwrites same-name files. [CITED: https://docs.python.org/3/library/pathlib.html]

**How to avoid:** Build "create missing only" helpers and assert sentinel content survives rerun. [VERIFIED: .planning/REQUIREMENTS.md]

**Warning signs:** Tests only check first-run output and do not mutate files before rerun. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py]

### Pitfall 2: Partial Writes Before Conflict Failure

**What goes wrong:** Init creates some directories, then discovers a required directory path is occupied by a file. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]

**Why it happens:** Implementation writes in traversal order instead of preflighting the full plan. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]

**How to avoid:** Compute `required_dirs` and `required_files`, detect all conflicts, and return nonzero before `mkdir` or file writes. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]

**Warning signs:** Conflict tests assert only return code, not that `.llm-wiki/` stayed absent or unchanged. [VERIFIED: .planning/REQUIREMENTS.md]

### Pitfall 3: Multi-Repo Parent Gets Initialized

**What goes wrong:** `.llm-wiki/` lands in a parent workspace that merely contains repos. [VERIFIED: .planning/PROJECT.md]

**Why it happens:** The command runs in a parent directory that is not the intended repo or the implementation adds `--target` too early. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]

**How to avoid:** Do not implement `--target`; when no Git root is resolved, report no-write failure and optional candidate child repos. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]

**Warning signs:** Tests cover clean repos but not non-git directories containing child Git repos. [VERIFIED: .planning/REQUIREMENTS.md]

### Pitfall 4: INIT-05 Scope Drift

**What goes wrong:** Planner implements seeding from `package.json`, `pyproject.toml`, `go.mod`, or `Cargo.toml` because requirements text mentions manifests. [VERIFIED: .planning/REQUIREMENTS.md]

**Why it happens:** Requirements predate the Phase 2 context decision that narrowed seeding to README/AGENTS. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]

**How to avoid:** Treat D-13 and D-14 as the controlling decision for Phase 2. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]

**Warning signs:** Tests create package manifests and expect `repo-overview.md` to summarize them. [VERIFIED: .planning/REQUIREMENTS.md]

### Pitfall 5: Empty Directories Do Not Appear In Git Status

**What goes wrong:** Required category directories are created but invisible in `git status`. [VERIFIED: .planning/REQUIREMENTS.md]

**Why it happens:** D-08 explicitly requires `.gitkeep` in otherwise-empty category directories so the complete skeleton appears in `git status`. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]

**How to avoid:** Add `.gitkeep` to otherwise-empty category directories as locked by D-08. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]

**Warning signs:** `.gitkeep` placeholders are missing from otherwise-empty required category directories. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]

### Pitfall 6: Dry-Run Has Side Effects

**What goes wrong:** `init --dry-run` creates directories while computing what would happen. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]

**Why it happens:** Dry-run uses the same helper that calls `mkdir` or writes files. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]

**How to avoid:** Separate plan construction from plan application and test that `.llm-wiki/` does not exist after dry-run. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]

**Warning signs:** Dry-run tests assert output but not filesystem state. [VERIFIED: .planning/REQUIREMENTS.md]

## Code Examples

Verified patterns from official sources and current repo context:

### Add `--dry-run` to the Existing Init Subcommand

```python
# Source: https://docs.python.org/3/library/argparse.html
init = subcommands.add_parser("init", help="initialize .llm-wiki in the current Git repo")
init.add_argument(
    "--dry-run",
    action="store_true",
    help="report planned changes without writing files",
)
init.set_defaults(func=run_init)
```

### Report Status Without Parsing Git Internals

```python
# Source: https://docs.python.org/3/library/subprocess.html
# Source: https://git-scm.com/docs/git-status
status = subprocess.run(
    ["git", "status", "--short"],
    cwd=repo,
    capture_output=True,
    text=True,
    check=False,
)
self.assertIn("?? .llm-wiki/", status.stdout)
```

### Generate a Minimal Seed Page

```python
# Source: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md
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

Planner note: keep this page light; init must not perform deep interpretation. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Phase 1 `init` returns "planned for Phase 2". [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py] | Phase 2 should implement real init behavior in the same helper. [VERIFIED: .planning/ROADMAP.md] | Phase 2 planning, 2026-05-13. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md] | Tests must change from "planned not mutating" to actual clean repo/init/idempotency assertions. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py] |
| Potential seed sources included package manifests in initial requirements. [VERIFIED: .planning/REQUIREMENTS.md] | Phase 2 seeds only from README.md and AGENTS.md. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md] | Phase 2 discussion, 2026-05-13. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md] | Planner must not implement manifest parsing in Phase 2. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md] |
| Template directory only had a placeholder README. [VERIFIED: skills/project-llm-wiki/assets/templates/README.md] | Phase 2 owns final skeleton templates and raw policy files. [VERIFIED: skills/project-llm-wiki/assets/templates/README.md] | Phase 2. [VERIFIED: skills/project-llm-wiki/assets/templates/README.md] | Add inspectable Markdown assets under `assets/templates/llm-wiki/`. [VERIFIED: skills/project-llm-wiki/assets/templates/README.md] |

**Deprecated/outdated:**

- The Phase 1 test `test_helper_init_is_planned_not_mutating` is obsolete once Phase 2 implements init. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py]
- The Phase 1 import whitelist allows only `argparse`, `pathlib`, `sys`, and `textwrap`; Phase 2 will need to update it if runtime code imports `subprocess` and possibly `dataclasses` or `typing`. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Shallow immediate-child repo discovery is enough for Phase 2 parent-workspace failure output. [ASSUMED] | Open Questions | If users run init from deeper workspace parents, candidate output may omit intended repos; init still must not write. |
| A2 | `init --dry-run` should return nonzero when conflicts would block a real run and zero when no conflicts exist. [ASSUMED] | Open Questions | If downstream tools expect dry-run to always return zero, scripts may need adjustment. |
| A3 | Research remains current for about 30 days for this stable stdlib/Git architecture. [ASSUMED] | Metadata | If Python or Git behavior changes sooner, planner may need to recheck docs before implementation. |

## Open Questions

1. **How deep should child repo candidate discovery search?**
   - What we know: D-02 says init may list candidate child git repos when discoverable. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]
   - What's unclear: The context does not lock search depth or hidden-directory handling. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]
   - Recommendation: Use shallow immediate-child discovery for Phase 2 and keep output concise. [ASSUMED]

2. **Should dry-run return success when conflicts exist?**
   - What we know: D-20 requires dry-run to report would-create, would-skip, and conflicts without writing. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]
   - What's unclear: The exact exit code is not locked. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]
   - Recommendation: Return nonzero when conflicts would block a real run; return zero when dry-run has no conflicts. [ASSUMED]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python 3 | Runtime helper and tests | yes [VERIFIED: python3 --version] | 3.14.3 [VERIFIED: python3 --version] | No fallback; project contract requires Python stdlib. [VERIFIED: .planning/PROJECT.md] |
| Git CLI | Root detection and fixture tests | yes [VERIFIED: git --version] | 2.50.1 (Apple Git-155) [VERIFIED: git --version] | No fallback for root detection because D-01 requires Git. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md] |
| ripgrep | Developer inspection only | yes [VERIFIED: rg --version] | 15.1.0 [VERIFIED: rg --version] | Use Python/std shell for tests; runtime must not require `rg`. [VERIFIED: .planning/PROJECT.md] |
| GSD SDK | Phase research and optional doc commit | yes [VERIFIED: gsd-sdk query init.phase-op "02"] | version not checked [VERIFIED: gsd-sdk query init.phase-op "02"] | Not required by Phase 2 runtime implementation. [VERIFIED: .planning/PROJECT.md] |

**Missing dependencies with no fallback:**

- None found for Phase 2 on this machine. [VERIFIED: python3 --version; VERIFIED: git --version]

**Missing dependencies with fallback:**

- None found for Phase 2 on this machine. [VERIFIED: python3 --version; VERIFIED: git --version]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python `unittest` with stdlib subprocess fixtures. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py; CITED: https://docs.python.org/3/library/unittest.html] |
| Config file | none. [VERIFIED: rg --files skills/project-llm-wiki .planning/phases/01-skill-package-foundation .planning/phases/02-init-and-wiki-templates] |
| Quick run command | `python3 -m unittest discover -s skills/project-llm-wiki/tests` [VERIFIED: skills/project-llm-wiki/references/testing.md] |
| Full suite command | `python3 -m unittest discover -s skills/project-llm-wiki/tests` [VERIFIED: skills/project-llm-wiki/references/testing.md] |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| INIT-01 | Running from repo subdirectory writes `.llm-wiki/` at Git root. [VERIFIED: .planning/REQUIREMENTS.md] | integration | `python3 -m unittest discover -s skills/project-llm-wiki/tests` [VERIFIED: skills/project-llm-wiki/references/testing.md] | no, Wave 0. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py] |
| INIT-02 | Non-git directory and parent-with-child-repo fail without writes. [VERIFIED: .planning/REQUIREMENTS.md] | integration | `python3 -m unittest discover -s skills/project-llm-wiki/tests` [VERIFIED: skills/project-llm-wiki/references/testing.md] | no, Wave 0. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py] |
| INIT-03 | Skeleton paths and `.gitkeep` placeholders are created. [VERIFIED: .planning/REQUIREMENTS.md] | integration | `python3 -m unittest discover -s skills/project-llm-wiki/tests` [VERIFIED: skills/project-llm-wiki/references/testing.md] | no, Wave 0. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py] |
| INIT-04 | Rerun does not overwrite sentinel-edited files. [VERIFIED: .planning/REQUIREMENTS.md] | integration | `python3 -m unittest discover -s skills/project-llm-wiki/tests` [VERIFIED: skills/project-llm-wiki/references/testing.md] | no, Wave 0. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py] |
| INIT-05 | `repo-overview.md` records README/AGENTS sources found or skipped, and ignores manifests. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md] | integration | `python3 -m unittest discover -s skills/project-llm-wiki/tests` [VERIFIED: skills/project-llm-wiki/references/testing.md] | no, Wave 0. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py] |
| INIT-06 | `git status --short` shows `.llm-wiki/` after clean repo init. [VERIFIED: .planning/REQUIREMENTS.md] | integration | `python3 -m unittest discover -s skills/project-llm-wiki/tests` [VERIFIED: skills/project-llm-wiki/references/testing.md] | no, Wave 0. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py] |
| RAW-01 | `raw/README.md` explains allowed and disallowed sources. [VERIFIED: .planning/REQUIREMENTS.md] | unit/content | `python3 -m unittest discover -s skills/project-llm-wiki/tests` [VERIFIED: skills/project-llm-wiki/references/testing.md] | no, Wave 0. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py] |
| RAW-02 | Raw policy forbids secrets and unsafe material. [VERIFIED: .planning/REQUIREMENTS.md] | unit/content | `python3 -m unittest discover -s skills/project-llm-wiki/tests` [VERIFIED: skills/project-llm-wiki/references/testing.md] | no, Wave 0. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py] |
| RAW-03 | `raw/curated/README.md` limits curated raw sources. [VERIFIED: .planning/REQUIREMENTS.md] | unit/content | `python3 -m unittest discover -s skills/project-llm-wiki/tests` [VERIFIED: skills/project-llm-wiki/references/testing.md] | no, Wave 0. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py] |
| TEST-01 | Clean repo init shows wiki files in Git status. [VERIFIED: .planning/REQUIREMENTS.md] | integration | `python3 -m unittest discover -s skills/project-llm-wiki/tests` [VERIFIED: skills/project-llm-wiki/references/testing.md] | no, Wave 0. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py] |
| TEST-02 | Clean repo rerun is idempotent. [VERIFIED: .planning/REQUIREMENTS.md] | integration | `python3 -m unittest discover -s skills/project-llm-wiki/tests` [VERIFIED: skills/project-llm-wiki/references/testing.md] | no, Wave 0. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py] |

### Sampling Rate

- **Per task commit:** `python3 -m unittest discover -s skills/project-llm-wiki/tests` [VERIFIED: skills/project-llm-wiki/references/testing.md]
- **Per wave merge:** `python3 -m unittest discover -s skills/project-llm-wiki/tests` [VERIFIED: skills/project-llm-wiki/references/testing.md]
- **Phase gate:** Full package test suite green before `$gsd-verify-work`. [VERIFIED: .planning/config.json]

### Wave 0 Gaps

- [ ] Extend `skills/project-llm-wiki/tests/test_project_wiki_package.py` or split into `test_project_wiki_init.py` for clean Git repo, subdirectory root detection, dry-run, conflict, and idempotency tests. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py]
- [ ] Update import whitelist expectations when runtime code adds `subprocess` and any other stdlib imports. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py]
- [ ] Add fixtures/helpers for temporary Git repositories using `tempfile.TemporaryDirectory`. [CITED: https://docs.python.org/3/library/tempfile.html]
- [ ] Add content assertions for raw policy templates and `features/ideas.md`. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | No authentication surface in Phase 2. [VERIFIED: .planning/ROADMAP.md] |
| V3 Session Management | no | No sessions in Phase 2. [VERIFIED: .planning/ROADMAP.md] |
| V4 Access Control | no | Local CLI writes only to the resolved Git root; no multi-user authorization model is introduced. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md] |
| V5 Input Validation | yes | Validate cwd via Git, reject path type conflicts, avoid `--target`, and use subprocess argument lists. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md; CITED: https://docs.python.org/3/library/subprocess.html] |
| V6 Cryptography | no | No cryptographic operation in Phase 2. [VERIFIED: .planning/ROADMAP.md] |

### Known Threat Patterns for Python CLI Init

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Unsafe raw material committed into `.llm-wiki/raw/` | Information Disclosure | Write explicit raw allow/deny templates now; defer scanning to Phase 3 lint. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md] |
| Init writes to the wrong repository or workspace parent | Tampering | Use `git rev-parse --show-toplevel`, reject non-target contexts, and do not add `--target`. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md; CITED: https://git-scm.com/docs/git-rev-parse] |
| Existing wiki notes overwritten | Tampering | Preflight paths and create missing files only. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md] |
| Shell injection through Git commands | Elevation of Privilege | Use `subprocess.run()` with an argument list and `shell=False`. [CITED: https://docs.python.org/3/library/subprocess.html] |
| Partial writes leave inconsistent skeleton | Tampering | Detect every path conflict before creating any path. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md] |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/02-init-and-wiki-templates/02-CONTEXT.md` - locked Phase 2 decisions, discretion, deferred ideas, current code context. [VERIFIED: file read]
- `.planning/REQUIREMENTS.md` - Phase 2 requirement IDs and descriptions. [VERIFIED: file read]
- `.planning/ROADMAP.md` - Phase 2 goal, success criteria, and plan split. [VERIFIED: file read]
- `.planning/STATE.md` - current project position and Phase 1 history. [VERIFIED: file read]
- `.planning/PROJECT.md` - project constraints and source-of-truth boundaries. [VERIFIED: file read]
- `AGENTS.md` - repo operating constraints and Lore commit protocol. [VERIFIED: file read]
- `skills/project-llm-wiki/scripts/project_wiki.py` - current helper implementation. [VERIFIED: file read]
- `skills/project-llm-wiki/tests/test_project_wiki_package.py` - current unittest patterns. [VERIFIED: file read]
- `skills/project-llm-wiki/assets/templates/README.md` - template ownership and safety rules. [VERIFIED: file read]
- Python docs for `argparse`, `pathlib`, `subprocess`, `tempfile`, and `unittest`. [CITED: https://docs.python.org/3/library/argparse.html; CITED: https://docs.python.org/3/library/pathlib.html; CITED: https://docs.python.org/3/library/subprocess.html; CITED: https://docs.python.org/3/library/tempfile.html; CITED: https://docs.python.org/3/library/unittest.html]
- Git docs for `git-rev-parse`, `git-status`, and `git-init`. [CITED: https://git-scm.com/docs/git-rev-parse; CITED: https://git-scm.com/docs/git-status; CITED: https://git-scm.com/docs/git-init]
- Local environment probes: `python3 --version`, `git --version`, `rg --version`, `python3 -m unittest discover -s skills/project-llm-wiki/tests`. [VERIFIED: command output]

### Secondary (MEDIUM confidence)

- None. [VERIFIED: source review]

### Tertiary (LOW confidence)

- Assumptions A1 through A3 in the Assumptions Log and Open Questions. [ASSUMED]

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - existing repo and project decisions require Python stdlib plus Git, and local versions were verified. [VERIFIED: .planning/PROJECT.md; VERIFIED: python3 --version; VERIFIED: git --version]
- Architecture: HIGH - Phase 2 context locks git-root behavior, idempotency, dry-run, and template ownership. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]
- Pitfalls: HIGH for idempotency/root/seed-scope pitfalls because they come from locked decisions and current code; MEDIUM for child repo discovery depth because exact discovery strategy remains discretionary. [VERIFIED: .planning/phases/02-init-and-wiki-templates/02-CONTEXT.md]
- Validation: HIGH - existing tests use `unittest` and the package test command is documented and currently passes. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py; VERIFIED: python3 -m unittest discover -s skills/project-llm-wiki/tests]

**Research date:** 2026-05-13
**Valid until:** 2026-06-12 for repo-local architecture; recheck Python/Git docs if implementation is delayed beyond 30 days. [ASSUMED]
