---
phase: 03-lint-and-safety-checks
plan: 01
subsystem: lint
tags: [python, unittest, markdown, wikilinks, safety]

requires:
  - phase: 02-init-and-wiki-templates
    provides: Safe git-root `.llm-wiki/` init and template skeleton
provides:
  - Real `project-wiki lint` entrypoint
  - Obsidian wikilink existence errors
  - Main wiki page index coverage warnings
  - Raw file byte-size warnings
affects: [phase-03, project-wiki-lint, llm-wiki]

tech-stack:
  added: []
  patterns:
    - Python stdlib subprocess fixture tests
    - Fixed lint finding dictionaries
    - Separate all-wiki and Markdown-only inventories

key-files:
  created:
    - skills/project-llm-wiki/tests/test_project_wiki_lint.py
  modified:
    - skills/project-llm-wiki/scripts/project_wiki.py
    - skills/project-llm-wiki/tests/test_project_wiki_package.py

key-decisions:
  - "Lint remains read-only and resolves the current Git root before inspecting `.llm-wiki/`."
  - "Broken Obsidian wikilinks are error findings; missing index coverage and oversized raw files are warning findings."
  - "Index coverage applies to main category pages plus `raw/README.md` and `raw/curated/README.md`, not other raw-curated source files."

patterns-established:
  - "Lint checks return fixed `severity`, `code`, `path`, `message`, and `remediation` fields before rendering text or JSON."
  - "Filesystem inventory skips symlinks and keeps all path resolution inside the resolved `.llm-wiki/` root."

requirements-completed: [LINT-01, LINT-02, LINT-04, TEST-04]

duration: 8m
completed: 2026-05-13T03:31:18Z
---

# Phase 03 Plan 01: Lint and Safety Checks Summary

**Repo-scoped `project-wiki lint` now reports broken Obsidian wikilinks, missing main index entries, and oversized raw files with deterministic findings**

## Performance

- **Duration:** 8m
- **Started:** 2026-05-13T03:23:12Z
- **Completed:** 2026-05-13T03:31:18Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Replaced the planned lint stub with a real read-only `project-wiki lint` command and stable `--json` flag.
- Added fixed-field lint findings for `broken_wikilink`, `unreadable_wiki_file`, `missing_index_entry`, and `oversized_raw_file`.
- Added 13 subprocess lint fixtures covering clean init, Obsidian link forms, path escape rejection, symlink skipping, unreadable files, index coverage, raw-curated policy handling, outgoing-link non-requirements, and raw-only size warnings.
- Preserved the package's standard-library-only contract by updating the import whitelist only for `json` and `re`.

## Task Commits

TDD gates were committed atomically:

1. **Task 1 RED: Wikilink lint fixtures** - `ee3bd4b`
2. **Task 1 GREEN: Read-only wikilink lint implementation** - `9164a13`
3. **Task 2 RED: Index coverage and raw-size fixtures** - `da21034`
4. **Task 2 GREEN: Index coverage and raw-size implementation** - `7d3cfc1`

## Files Created/Modified

- `skills/project-llm-wiki/tests/test_project_wiki_lint.py` - New subprocess fixture suite for Phase 03 lint behavior.
- `skills/project-llm-wiki/scripts/project_wiki.py` - Real lint pipeline, inventories, finding helpers, wikilink parser, index coverage, and raw file size checks.
- `skills/project-llm-wiki/tests/test_project_wiki_package.py` - Import whitelist updated for the new stdlib-only lint imports.

## Decisions Made

- Lint uses separate `collect_wiki_files` and `collect_markdown_files` helpers so later all-wiki safety checks cannot accidentally depend on Markdown-only inventory.
- Parent-directory and absolute wikilink targets are reported as `broken_wikilink` errors instead of being resolved against the repository filesystem.
- Warning-only findings keep exit code `0`; only `severity == "error"` findings make lint exit `1`.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The commit hook rejected a compact multi-trailer commit message. Resolved by using the repository's blank-line-separated Lore trailer format with the required OmX co-author trailer.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_lint.py` - 13 tests passed.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_package.py` - 8 tests passed.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests` - 35 tests passed.
- `python3 skills/project-llm-wiki/scripts/project_wiki.py lint --help` - showed `--json`.
- `git diff --check` - passed.

## TDD Gate Compliance

- RED gate present for Task 1: `ee3bd4b`.
- GREEN gate present for Task 1: `9164a13`.
- RED gate present for Task 2: `da21034`.
- GREEN gate present for Task 2: `7d3cfc1`.

## User Setup Required

None - no external service configuration required.

## Auth Gates

None.

## Next Phase Readiness

Plan 03-02 can extend the existing lint pipeline with all-wiki secret-looking checks, stale frontmatter warnings, and conservative repo-path drift warnings. The inventory split and fixed finding shape are already in place for those additions.

## Self-Check: PASSED

- Summary file exists at `.planning/phases/03-lint-and-safety-checks/03-01-SUMMARY.md`.
- Created and modified files exist at the expected paths.
- Task commits exist: `ee3bd4b`, `9164a13`, `da21034`, `7d3cfc1`.
- No unexpected tracked file deletions were detected after task commits.

---
*Phase: 03-lint-and-safety-checks*
*Completed: 2026-05-13*
