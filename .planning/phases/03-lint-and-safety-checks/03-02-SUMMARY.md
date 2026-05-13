---
phase: 03-lint-and-safety-checks
plan: 02
subsystem: lint
tags: [python, unittest, markdown, safety, freshness]

requires:
  - phase: 03-lint-and-safety-checks
    provides: Plan 03-01 lint pipeline, fixed finding shape, and all-wiki/Markdown inventory split
provides:
  - High-confidence secret-looking lint warnings across all regular `.llm-wiki/` files
  - Stale `updated:` frontmatter warnings for pages older than 90 days
  - Conservative missing repo path drift warnings from code spans and fenced blocks
affects: [phase-03, project-wiki-lint, llm-wiki-safety]

tech-stack:
  added: []
  patterns:
    - Python stdlib regex safety checks
    - Top-of-file frontmatter date parsing
    - Code-span-only repo path drift detection

key-files:
  created: []
  modified:
    - skills/project-llm-wiki/scripts/project_wiki.py
    - skills/project-llm-wiki/tests/test_project_wiki_lint.py
    - skills/project-llm-wiki/tests/test_project_wiki_package.py

key-decisions:
  - "Secret-looking lint scans the `collect_wiki_files(git_root)` inventory, including non-Markdown raw files, and stays warning-only."
  - "Secret heuristics are limited to private key delimiters and credential-bearing URLs to avoid raw policy false positives."
  - "Repo path drift inspects only inline code spans and fenced code block lines, then checks only root-confined relative candidates."

patterns-established:
  - "All warning-only safety, stale, size, and path-drift findings keep lint exit code 0."
  - "Path drift ignores prose, `.llm-wiki/` internal paths, outside-repo paths, URLs, home paths, and directory-style trailing-slash examples."

requirements-completed: [LINT-03, LINT-05, LINT-06, TEST-05]

duration: 9m
completed: 2026-05-13T03:46:25Z
---

# Phase 03 Plan 02: Lint and Safety Checks Summary

**Warning-only safety, stale-page, and repo path drift lint checks now cover all wiki files without semantic guessing or automatic edits**

## Performance

- **Duration:** 9m
- **Started:** 2026-05-13T03:37:23Z
- **Completed:** 2026-05-13T03:46:25Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Added high-confidence `secret_like_content` warnings for private key delimiters and credential-bearing URLs across every regular file from `collect_wiki_files(git_root)`, including non-`.md` raw files.
- Added `stale_page` warnings from top-of-file `updated: YYYY-MM-DD` frontmatter older than 90 days, with read-only remediation.
- Added `missing_repo_path` warnings for missing root-confined relative paths found only in Markdown code spans and fenced code blocks.
- Expanded subprocess fixtures to prove warning-only exit behavior, raw policy false-positive protection, symlink skipping, unreadable all-file scan errors, stale-page behavior, and path-drift boundaries.

## Task Commits

TDD gates were committed atomically:

1. **Task 1 RED: Secret-looking and stale-page fixtures** - `7758ebe`
2. **Task 1 GREEN: All-file secret and stale frontmatter implementation** - `51e0b2b`
3. **Task 2 RED: Conservative repo path drift fixtures** - `f8ea82a`
4. **Task 2 GREEN: Code-reference path drift implementation** - `97fab28`

## Files Created/Modified

- `skills/project-llm-wiki/scripts/project_wiki.py` - Added secret-like scanning, stale frontmatter parsing, code reference extraction, repo path candidate filtering, and drift warnings.
- `skills/project-llm-wiki/tests/test_project_wiki_lint.py` - Added 16 subprocess fixtures for Task 1 and Task 2 lint behavior.
- `skills/project-llm-wiki/tests/test_project_wiki_package.py` - Added `datetime` to the stdlib import whitelist used by stale checks.

## Decisions Made

- Kept secret detection deliberately narrow: private key block headers and credential-bearing URLs only.
- Treated unreadable files encountered during all-file secret scanning as `unreadable_wiki_file` error findings instead of operational exit 2.
- Ignored directory-style code references ending in `/`, because default wiki index category examples are not repo file claims.
- Reused `path_is_under` with `resolve(strict=False)` before checking candidate path existence.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed stale remediation wording mismatch**
- **Found during:** Task 1 GREEN
- **Issue:** The stale-page remediation initially used capitalized wording that failed the planned lowercase output assertion.
- **Fix:** Aligned remediation text with the fixture and plan wording.
- **Files modified:** `skills/project-llm-wiki/scripts/project_wiki.py`
- **Verification:** Targeted lint suite passed after the fix.
- **Committed in:** `51e0b2b`

**2. [Rule 1 - Bug] Prevented default index directory examples from triggering path drift**
- **Found during:** Task 2 GREEN
- **Issue:** The first path candidate filter treated default code spans such as `architecture/` and `raw/curated/` as missing repo paths.
- **Fix:** Ignored trailing-slash directory-style references before path existence checks.
- **Files modified:** `skills/project-llm-wiki/scripts/project_wiki.py`
- **Verification:** Targeted and full suites passed after the fix.
- **Committed in:** `97fab28`

---

**Total deviations:** 2 auto-fixed (Rule 1 bugs).
**Impact on plan:** No scope expansion. Both fixes were required to preserve the warning-only, low-noise lint contract.

## Issues Encountered

- The path drift implementation was initially too broad for default template index examples. The candidate filter now requires file-like relative references and ignores trailing-slash directory examples.

## Known Stubs

None.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_lint.py` - 29 tests passed.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_package.py` - 8 tests passed.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests` - 51 tests passed.
- Task 1 and Task 2 `rg` acceptance checks - passed.
- `git diff --check` - passed.

## TDD Gate Compliance

- RED gate present for Task 1: `7758ebe`.
- GREEN gate present for Task 1: `51e0b2b`.
- RED gate present for Task 2: `f8ea82a`.
- GREEN gate present for Task 2: `97fab28`.

## User Setup Required

None - no external service configuration required.

## Auth Gates

None.

## Next Phase Readiness

Plan 03-03 can build on the completed finding codes `secret_like_content`, `stale_page`, and `missing_repo_path` to finish actionable output formatting and final lint fixture coverage.

## Self-Check: PASSED

- Summary file exists at `.planning/phases/03-lint-and-safety-checks/03-02-SUMMARY.md`.
- Modified files exist at the expected paths.
- Task commits exist: `7758ebe`, `51e0b2b`, `f8ea82a`, `97fab28`.
- No unexpected tracked file deletions were detected after task commits.
- Unrelated `AGENTS.md` changes were not staged or committed.

---
*Phase: 03-lint-and-safety-checks*
*Completed: 2026-05-13*
