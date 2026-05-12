---
phase: 02-init-and-wiki-templates
reviewed: 2026-05-12T23:33:17Z
depth: standard
files_reviewed: 12
files_reviewed_list:
  - skills/project-llm-wiki/scripts/project_wiki.py
  - skills/project-llm-wiki/tests/test_project_wiki_package.py
  - skills/project-llm-wiki/tests/test_project_wiki_init.py
  - skills/project-llm-wiki/references/testing.md
  - skills/project-llm-wiki/assets/templates/README.md
  - skills/project-llm-wiki/assets/templates/llm-wiki/README.md
  - skills/project-llm-wiki/assets/templates/llm-wiki/AGENTS.md
  - skills/project-llm-wiki/assets/templates/llm-wiki/index.md
  - skills/project-llm-wiki/assets/templates/llm-wiki/log.md
  - skills/project-llm-wiki/assets/templates/llm-wiki/raw/README.md
  - skills/project-llm-wiki/assets/templates/llm-wiki/raw/curated/README.md
  - skills/project-llm-wiki/assets/templates/llm-wiki/features/ideas.md
findings:
  critical: 1
  warning: 2
  info: 0
  total: 3
status: issues_found
---

# Phase 02: Code Review Report

**Reviewed:** 2026-05-12T23:33:17Z
**Depth:** standard
**Files Reviewed:** 12
**Status:** issues_found

## Summary

Reviewed the Phase 2 init helper, subprocess tests, testing reference, and wiki template assets against the locked init/template requirements. The normal path is covered by the package suite (`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests`, 16 tests passing), and the templates generally match the raw-source and durable-knowledge boundaries.

The implementation still has a blocker in path preflight: symlinked required paths can cause init writes outside the resolved git root. Two additional requirement/coverage gaps remain around dry-run conflict reporting and runtime skeleton assertions.

## Critical Issues

### CR-01: Symlinked Wiki Paths Can Escape the Resolved Git Root

**Severity:** BLOCKER
**File:** `skills/project-llm-wiki/scripts/project_wiki.py:155-169`, `skills/project-llm-wiki/scripts/project_wiki.py:194-198`
**Issue:** `find_init_conflicts` treats symlinked directories as valid directories and treats broken symlinks as missing because it relies on `exists()`, `is_dir()`, and `is_file()`. `create_file_if_missing` then calls `write_text()` on the required wiki path. A broken symlink at `.llm-wiki/README.md` pointing outside the repo is considered missing and gets written through the symlink; a symlinked `.llm-wiki/` or `.llm-wiki/raw/` directory can similarly redirect generated files outside `git_root`. This violates the Phase 2 repository-boundary requirement and can write outside the intended repository while reporting success.
**Fix:**
```python
def path_is_under(path: pathlib.Path, root: pathlib.Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve())
        return True
    except ValueError:
        return False


def find_init_conflicts(git_root: pathlib.Path) -> list[str]:
    conflicts: list[str] = []
    for relative_path in REQUIRED_DIRECTORIES:
        path = git_root / relative_path
        if path.is_symlink():
            conflicts.append(f"{relative_path.as_posix()}: expected real directory, found symlink")
        elif path.exists() and not path.is_dir():
            conflicts.append(f"{relative_path.as_posix()}: expected directory, found file")
    for relative_path in REQUIRED_FILES:
        path = git_root / relative_path
        if path.is_symlink():
            conflicts.append(f"{relative_path.as_posix()}: expected real file, found symlink")
        elif path.exists() and not path.is_file():
            conflicts.append(f"{relative_path.as_posix()}: expected file, found directory")
        elif not path_is_under(path, git_root):
            conflicts.append(f"{relative_path.as_posix()}: resolves outside git root")
    return conflicts
```
Also add regression tests for a broken symlinked required file and a symlinked required directory before any writes occur.

## Warnings

### WR-01: Conflict Dry Runs Do Not Report the Planned Create/Skip Sets

**Severity:** WARNING
**File:** `skills/project-llm-wiki/scripts/project_wiki.py:264-282`
**Issue:** Phase decision D-20 requires `--dry-run` to report would-create, would-skip, and conflicts without writing. The current flow returns immediately when `find_init_conflicts()` finds a conflict, so `project-wiki init --dry-run` with a blocking path conflict prints only `Conflicts:` and omits the `Would create paths:` and `Would skip existing paths:` sections. The existing dry-run test covers only the no-conflict path.
**Fix:** Build the create/skip plan before returning for dry-run conflicts, print all three dry-run sections, and return nonzero after reporting.
```python
would_create, would_skip = collect_init_paths(git_root)
if args.dry_run:
    print_path_section("Would create paths:", would_create)
    print_path_section("Would skip existing paths:", would_skip)
    if conflicts:
        print_text_section("Conflicts:", conflicts)
        return 2
    ...
```
Add a test that creates a required path conflict, runs `init --dry-run`, asserts no writes, and checks for all three headings.

### WR-02: Runtime Skeleton Tests Do Not Assert All Required Files

**Severity:** WARNING
**File:** `skills/project-llm-wiki/tests/test_project_wiki_init.py:64-75`
**Issue:** The integration test checks many generated paths but omits `.llm-wiki/AGENTS.md` and `.llm-wiki/log.md`, both of which are required by Phase 2 D-07 and included in the template inventory. A regression that removed either file from `REQUIRED_FILES` could still pass the init integration coverage as long as the template asset remained listed elsewhere.
**Fix:** Replace the individual path assertions with an explicit required-files list that includes every required runtime file and directory, especially `.llm-wiki/AGENTS.md` and `.llm-wiki/log.md`.
```python
expected_files = [
    ".llm-wiki/README.md",
    ".llm-wiki/AGENTS.md",
    ".llm-wiki/index.md",
    ".llm-wiki/log.md",
    ".llm-wiki/raw/README.md",
    ".llm-wiki/raw/curated/README.md",
    ".llm-wiki/features/ideas.md",
    ".llm-wiki/summaries/repo-overview.md",
]
for relative_path in expected_files:
    self.assertTrue((repo / relative_path).is_file(), relative_path)
```

---

_Reviewed: 2026-05-12T23:33:17Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
