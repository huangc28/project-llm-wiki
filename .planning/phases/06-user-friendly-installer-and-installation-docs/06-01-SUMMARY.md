---
phase: 06-user-friendly-installer-and-installation-docs
plan: 01
subsystem: packaging
tags: [codex-skills, installer, symlinks, docs, unittest]

requires:
  - phase: 05-agents-integration-and-real-repo-validation
    provides: AGENTS patching and target-repo init boundary
provides:
  - One-command public install bootstrap
  - Safe `project-wiki install` helper mode
  - Installer safety regression tests
  - Installer-first README and command reference docs
affects: [skills, packaging, onboarding, docs]

tech-stack:
  added: []
  patterns:
    - Python stdlib CLI planning all filesystem writes before applying them
    - POSIX shell bootstrap that only clones or updates then delegates

key-files:
  created:
    - install.sh
    - skills/project-llm-wiki/tests/test_project_wiki_install.py
  modified:
    - README.md
    - skills/project-llm-wiki/scripts/project_wiki.py
    - skills/project-llm-wiki/tests/test_project_wiki_package.py
    - skills/project-llm-wiki/references/command-surface.md
    - skills/project-llm-wiki/references/package-contract.md

key-decisions:
  - "Lead README install with `curl -fsSL ... | bash`; keep manual symlink instructions as fallback only."
  - "Install manages only Codex skill symlinks; repo mutation remains behind `project-wiki init`."
  - "Use symlinks instead of copying so updates come from the package checkout."

patterns-established:
  - "Installer commands must preflight conflicts before writing any symlink."
  - "Uninstall removes only symlinks resolving inside the package source root."

requirements-completed:
  - INSTALL-01
  - INSTALL-02
  - INSTALL-03
  - INSTALL-04
  - INSTALL-05
  - INSTALL-06
  - TEST-08
  - TEST-09
  - TEST-10

duration: 21min
completed: 2026-05-15
---

# Phase 6 Plan 1: User-Friendly Installer Summary

**One-command Codex skill installer with safe symlink planning, uninstall support, and installer-first onboarding docs**

## Performance

- **Duration:** 21 min
- **Started:** 2026-05-15T19:32:00+08:00
- **Completed:** 2026-05-15T19:53:27+08:00
- **Tasks:** 4
- **Files modified:** 10 implementation/docs/tests plus GSD planning artifacts

## Accomplishments

- Added `project-wiki install` with `--target`, `--dry-run`, `--force`, and `--uninstall`.
- Added root `install.sh` that clones or updates the package, then delegates policy to the Python helper.
- Reworked README and references so the primary user path is one command, restart Codex, then `$project-wiki-init`.
- Added installer regression tests for idempotency, conflicts, stale symlinks, uninstall ownership, and install/init boundary separation.

## Task Commits

Inline execution was consolidated into the final phase commit; no per-task commits were created.

## Files Created/Modified

- `install.sh` - Public bootstrap that clones or updates the package and calls `project_wiki.py install`.
- `skills/project-llm-wiki/scripts/project_wiki.py` - Adds the install subcommand and symlink safety planner.
- `skills/project-llm-wiki/tests/test_project_wiki_install.py` - Locks installer safety behavior with temp-directory tests.
- `skills/project-llm-wiki/tests/test_project_wiki_package.py` - Extends package/docs assertions for installer help and README flow.
- `README.md` - Leads with one-command install and moves manual symlinks to advanced fallback.
- `skills/project-llm-wiki/references/command-surface.md` - Documents installer examples and write boundaries.
- `skills/project-llm-wiki/references/package-contract.md` - States install owns global Codex skill symlinks while init owns repo mutation.

## Decisions Made

- Default install target is `${CODEX_HOME:-~/.codex}/skills`.
- Missing Codex home is a conflict; the helper can create the `skills` directory only when its parent exists.
- Existing real files or directories are never overwritten.
- Wrong symlinks require `--force`; correct symlinks are no-ops.
- `--uninstall` preserves foreign symlinks and real directories.

## Deviations from Plan

- README dry-run examples use `bash -s -- --dry-run` so the primary command remains `curl ... | bash` while still passing installer flags.

**Total deviations:** 1 documentation syntax adjustment.
**Impact on plan:** No scope change; it keeps the exact primary install command while preserving flag forwarding.

## Issues Encountered

- Initial installer tests failed as expected because `install` did not exist yet.
- Full suite was re-run after a formatting-only helper cleanup so final verification reflects the current diff.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_install.py` - 7 tests, OK.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_package.py` - 24 tests, OK.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests` - 154 tests in 155.489s, OK.
- `python3 skills/project-llm-wiki/scripts/project_wiki.py install --help` - exits 0 and documents all install flags.
- `rg -n "curl -fsSL https://raw.githubusercontent.com/huangc28/project-llm-wiki/main/install.sh \\| bash|Restart Codex|\\$project-wiki-init" README.md` - found required README onboarding anchors.
- `git diff --check` - clean.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 6 is complete and ready for review or release packaging. The only unverified path is live network execution of the curl bootstrap, which was not run from the restricted sandbox.

---
*Phase: 06-user-friendly-installer-and-installation-docs*
*Completed: 2026-05-15*
