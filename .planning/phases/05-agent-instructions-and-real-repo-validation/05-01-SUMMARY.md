---
phase: 05-agent-instructions-and-real-repo-validation
plan: 01
subsystem: cli-testing
tags: [python, unittest, agents-md, init, project-wiki]

requires:
  - phase: 04-query-and-ingest-loop
    provides: repo-local query and ingest boundaries that the root AGENTS.md guidance references
provides:
  - marker-bounded root AGENTS.md patch planning for project-wiki init
  - default safe root AGENTS.md create, append, update, dry-run, and opt-out behavior
  - preservation-focused subprocess fixtures for NotebookLM, GSD, workflow, and repo-specific AGENTS sections
affects: [phase-05, project-wiki-init, agent-instructions]

tech-stack:
  added: []
  patterns:
    - pure plan-then-apply filesystem mutation
    - marker-bounded text replacement preserving external bytes
    - subprocess unittest fixtures against temporary Git repositories

key-files:
  created:
    - .planning/phases/05-agent-instructions-and-real-repo-validation/05-01-SUMMARY.md
  modified:
    - skills/project-llm-wiki/scripts/project_wiki.py
    - skills/project-llm-wiki/tests/test_project_wiki_init.py
    - skills/project-llm-wiki/tests/test_project_wiki_package.py

key-decisions:
  - "Root AGENTS.md patching is part of project-wiki init by default, with --no-patch-agents as the explicit opt-out."
  - "Dry-run and apply share one AGENTS patch plan so conflict behavior cannot diverge between preview and write paths."
  - "Existing root AGENTS.md files are updated only through the exact PROJECT-LLM-WIKI marker span; marker-external bytes remain authoritative user content."

patterns-established:
  - "AGENTS patch planner: build_agents_patch_plan returns enabled, relative_path, action, content, and conflicts for dry-run/apply reuse."
  - "Root managed section: concise protocol text points agents to .llm-wiki/index.md only for non-trivial work and keeps active task state out of the wiki."
  - "Conflict-first init: invalid UTF-8, unmatched markers, duplicate marker pairs, symlink, directory, or root escape conflicts stop before .llm-wiki writes."

requirements-completed: [AGENT-01, AGENT-02, AGENT-03, AGENT-04, AGENT-05, TEST-06]

duration: 8m
completed: 2026-05-14
---

# Phase 05 Plan 01: Marker-Bounded AGENTS Patching Summary

**Default project-wiki init now safely creates, appends, updates, dry-runs, or skips root AGENTS.md Project LLM Wiki guidance while preserving unrelated instructions.**

## Performance

- **Duration:** 8 min
- **Started:** 2026-05-14T06:02:18Z
- **Completed:** 2026-05-14T06:10:10Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- Added RED fixtures for missing root `AGENTS.md`, markerless append, marker-bounded update, dry-run no-write, `--no-patch-agents`, invalid UTF-8, unmatched markers, duplicate markers, and byte-preservation cases.
- Implemented root `AGENTS.md` patch planning in `project_wiki.py` with exact Project LLM Wiki markers and conflict messages.
- Wired `project-wiki init --dry-run` and normal init to use the same AGENTS patch plan before any `.llm-wiki/` writes.
- Verified targeted init/package suites and the full package suite.

## Task Commits

1. **Task 1: Add root AGENTS patch fixture coverage** - `d824ef3`
2. **Task 2: Implement marker-bounded root AGENTS patching** - `8b01ff7`
3. **Task 3: Run Phase 5 patching gates** - `29716c5` (empty verification commit)

## Files Created/Modified

- `skills/project-llm-wiki/tests/test_project_wiki_init.py` - Adds subprocess fixtures for root `AGENTS.md` patching, dry-run/no-write behavior, opt-out, marker conflicts, and byte preservation.
- `skills/project-llm-wiki/tests/test_project_wiki_package.py` - Adds init help coverage for `--dry-run` and `--no-patch-agents`.
- `skills/project-llm-wiki/scripts/project_wiki.py` - Adds root AGENTS constants, managed section rendering, patch planning, dry-run rendering, apply behavior, and init CLI flag wiring.
- `.planning/phases/05-agent-instructions-and-real-repo-validation/05-01-SUMMARY.md` - Records plan outcome and verification evidence.

## Decisions Made

- Root `AGENTS.md` remains outside the `.llm-wiki/` skeleton list and is handled by a separate patch plan because it has different conflict and preservation semantics.
- The managed section is rendered from code as a short fixed protocol block rather than copying the wiki-local `AGENTS.md` template wholesale.
- `--no-patch-agents` skips only root `AGENTS.md`; it does not skip `.llm-wiki/` skeleton creation.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests -p "test_project_wiki_init.py"` - PASS, 23 tests.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests -p "test_project_wiki_package.py"` - PASS, 18 tests.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests` - PASS, 139 tests.
- `rg` acceptance checks for Task 1 test names, Task 2 helper contracts, dry-run strings, flag strings, and conflict messages - PASS.

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None. Stub scan only found pre-existing parser defaults and placeholder-secret detection constants; no UI/data-source stubs were introduced.

## Threat Flags

None. The new root `AGENTS.md` write surface is the planned T-05-01 through T-05-05 surface and is covered by conflict preflight plus preservation tests.

## Issues Encountered

- A parallel `git add` attempt briefly hit a stale `.git/index.lock`; no git process was active by the time it was checked, the lock had cleared, and staging continued serially. No repository content was affected.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plan 05-02 can dry-run validate this implementation against `peasydeal_be` without writing to that target repo. The package suite is green and the root `AGENTS.md` managed-section behavior is covered by subprocess fixtures.

## Self-Check: PASSED

- Summary file exists at `.planning/phases/05-agent-instructions-and-real-repo-validation/05-01-SUMMARY.md`.
- Task commits verified: `d824ef3`, `8b01ff7`, `29716c5`.
- No tracked file deletions were present in task commits.

---
*Phase: 05-agent-instructions-and-real-repo-validation*
*Completed: 2026-05-14*
