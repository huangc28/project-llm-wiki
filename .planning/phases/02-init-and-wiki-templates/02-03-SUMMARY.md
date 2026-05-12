---
phase: 02-init-and-wiki-templates
plan: 03
subsystem: testing
tags: [python, unittest, git, red-validation, llm-wiki]

requires:
  - phase: 01-skill-package-foundation
    provides: reusable Project LLM Wiki package, helper command surface, baseline tests
provides:
  - Wave 0 RED validation fixtures for project-wiki-init
  - Phase 2 testing reference with RED and future green commands
  - Executable coverage for git-root safety, idempotency, seed-source limits, and raw policy expectations
affects: [02-init-and-wiki-templates, project-wiki-init, tests]

tech-stack:
  added: []
  patterns: [Python unittest subprocess fixtures, temporary Git repositories, RED gate wrapper]

key-files:
  created:
    - skills/project-llm-wiki/tests/test_project_wiki_init.py
  modified:
    - skills/project-llm-wiki/references/testing.md

key-decisions:
  - "Plan 02-03 intentionally remains RED-only; Plans 02-01 and 02-02 own the GREEN transition."
  - "README.md and AGENTS.md are the only seed sources asserted by the RED fixtures; language manifests are explicitly excluded."

patterns-established:
  - "Init integration tests execute project_wiki.py as a subprocess from temporary Git repositories."
  - "The RED gate exits 0 only while the suite contains expected failing init behavior."

requirements-completed: []
requirements-validated-red:
  - INIT-01
  - INIT-02
  - INIT-03
  - INIT-04
  - INIT-05
  - INIT-06
  - RAW-01
  - RAW-02
  - RAW-03
  - TEST-01
  - TEST-02

duration: 5m28s
completed: 2026-05-13
---

# Phase 02 Plan 03: Wave 0 RED Validation Fixtures Summary

**RED validation fixtures now define the init safety, skeleton, seed-source, raw policy, git visibility, and idempotency contract before implementation.**

## Performance

- **Duration:** 5m28s
- **Started:** 2026-05-12T22:54:19Z
- **Completed:** 2026-05-12T22:59:47Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Added `test_project_wiki_init.py` with temporary Git repo subprocess fixtures for clean init, nested cwd root targeting, parent workspace refusal, dry-run behavior, conflict preflight, git status visibility, idempotency, seed-source limits, raw policy content, and ideas-page fields.
- Updated `testing.md` from Phase 1 import-only wording to the Phase 2 validation contract with the exact RED gate and future green test command.
- Preserved production behavior: `project_wiki.py` remains unmodified, so the new suite is intentionally RED for later implementation plans.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add clean git repo, subdirectory, dry-run, parent-refusal, and conflict tests** - `f4cb8b8` (test)
2. **Task 2: Add idempotency, git-status, raw policy, and seed-source tests** - `1c10de5` (test)

**Plan metadata:** committed separately after this summary.

## Files Created/Modified

- `skills/project-llm-wiki/tests/test_project_wiki_init.py` - RED integration tests for Phase 2 init behavior.
- `skills/project-llm-wiki/references/testing.md` - Phase 2 validation contract and test commands.

## Decisions Made

- Kept Plan 02-03 RED-only. No production code was changed because later plans own the implementation and GREEN transition.
- Did not update `test_project_wiki_package.py` because `project_wiki.py` imports did not change during this plan.
- Did not mark Phase 2 implementation requirements complete; this plan validates them with RED fixtures rather than delivering the runtime behavior.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- Test runs generated `skills/project-llm-wiki/tests/__pycache__/`; it was removed after verification and not committed.

## Verification

- Task 1 acceptance checks passed:
  - `test -f skills/project-llm-wiki/tests/test_project_wiki_init.py`
  - `rg -n "test_init_creates_wiki_at_git_root_from_subdirectory|test_init_refuses_parent_workspace_with_child_repo_candidate|test_dry_run_reports_without_writing|test_conflict_fails_before_partial_writes" skills/project-llm-wiki/tests/test_project_wiki_init.py`
  - `rg -n "git\", \"init|git\", \"status\", \"--short|TemporaryDirectory" skills/project-llm-wiki/tests/test_project_wiki_init.py`
  - RED gate wrapper exited 0 with four expected failures.
- Task 2 acceptance checks passed:
  - `rg -n "test_clean_repo_status_shows_llm_wiki_files|test_rerun_preserves_existing_files_and_reports_missing_index_links|test_repo_overview_uses_only_readme_and_agents|test_raw_policy_and_ideas_content" skills/project-llm-wiki/tests/test_project_wiki_init.py`
  - `rg -n "package\\.json|pyproject\\.toml|go\\.mod|Cargo\\.toml" skills/project-llm-wiki/tests/test_project_wiki_init.py`
  - `rg -n "secrets, credentials, auth tokens, private customer data, full logs, database exports, generated dumps|2026-05-13-api-notes.md" skills/project-llm-wiki/tests/test_project_wiki_init.py`
  - `rg -n "clean temporary Git repositories|git status --short|init --dry-run|idempotency|raw policy content" skills/project-llm-wiki/references/testing.md`
  - RED gate wrapper exited 0 with eight expected failures.
- Plan-level verification passed: the RED gate command exited 0 because the full suite is still intentionally failing against the current unimplemented helper.

## TDD Gate Compliance

This plan is a RED validation plan by design. It produced two `test(02-03)` commits and intentionally no `feat(02-03)` commit; Plans 02-01 and 02-02 own the GREEN transition.

## Known Stubs

None. The failing tests are intentional RED fixtures, not shipped runtime stubs.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Ready for Plan 02-01 to implement git-root detection, parent workspace refusal, dry-run behavior, and conflict preflight against the RED fixtures. Plan 02-02 can then add skeleton templates, repo overview seeding, and raw policy content until the full Phase 2 suite turns green.

## Self-Check: PASSED

- Created file exists: `skills/project-llm-wiki/tests/test_project_wiki_init.py`
- Modified reference exists: `skills/project-llm-wiki/references/testing.md`
- Task commits found: `f4cb8b8`, `1c10de5`
- RED gate verified after both commits: wrapper exited 0 with eight expected failures.
- Unrelated dirty `AGENTS.md` remained unstaged and untouched.

---
*Phase: 02-init-and-wiki-templates*
*Completed: 2026-05-13*
