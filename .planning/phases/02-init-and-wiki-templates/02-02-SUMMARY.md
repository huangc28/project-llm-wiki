---
phase: 02-init-and-wiki-templates
plan: 02
subsystem: init-templates
tags: [python, unittest, git, markdown, llm-wiki]

requires:
  - phase: 01-skill-package-foundation
    provides: reusable Project LLM Wiki package, helper command surface, baseline tests
  - phase: 02-init-and-wiki-templates
    provides: init safety control plane and Wave 0 RED validation fixtures
provides:
  - Inspectable `.llm-wiki/` Markdown template assets
  - README/AGENTS-only repo overview seeding
  - Template-backed init skeleton with `.gitkeep` placeholders and raw source policy
affects: [02-init-and-wiki-templates, project-wiki-init, phase-03-lint]

tech-stack:
  added: []
  patterns: [static Markdown template loading, provenance-only seed generation, missing-only init writes]

key-files:
  created:
    - skills/project-llm-wiki/assets/templates/llm-wiki/README.md
    - skills/project-llm-wiki/assets/templates/llm-wiki/AGENTS.md
    - skills/project-llm-wiki/assets/templates/llm-wiki/index.md
    - skills/project-llm-wiki/assets/templates/llm-wiki/log.md
    - skills/project-llm-wiki/assets/templates/llm-wiki/raw/README.md
    - skills/project-llm-wiki/assets/templates/llm-wiki/raw/curated/README.md
    - skills/project-llm-wiki/assets/templates/llm-wiki/features/ideas.md
    - .planning/phases/02-init-and-wiki-templates/02-02-SUMMARY.md
  modified:
    - skills/project-llm-wiki/scripts/project_wiki.py
    - skills/project-llm-wiki/assets/templates/README.md
    - skills/project-llm-wiki/tests/test_project_wiki_package.py

key-decisions:
  - "The default wiki skeleton lives in inspectable Markdown assets under `assets/templates/llm-wiki/`."
  - "Repo overview seeding records README.md and AGENTS.md presence only; it does not parse or summarize source content."
  - "Generated `.gitkeep` files are supplied by init content mapping rather than static package assets."

patterns-established:
  - "Init file content is assembled from static template contents plus generated repo overview and `.gitkeep` entries."
  - "Dry-run and real init both report `Sources found:` and `Skipped sources:` without changing existing wiki notes."

requirements-completed: [INIT-03, INIT-05, RAW-01, RAW-02, RAW-03]

duration: 7m
completed: 2026-05-12
---

# Phase 02 Plan 02: Wiki Templates and Seed Generation Summary

**Template-backed `.llm-wiki/` init with raw policy pages, durable ideas, and README/AGENTS provenance seeding**

## Performance

- **Duration:** 7m
- **Started:** 2026-05-12T23:18:52Z
- **Completed:** 2026-05-12T23:25:48Z
- **Tasks:** 2
- **Files modified:** 11

## Accomplishments

- Added the complete default `.llm-wiki/` template set: README, AGENTS notes, index, log, raw policy, curated raw policy, and durable ideas page.
- Updated init to load package template assets, generate `.llm-wiki/summaries/repo-overview.md`, and create empty category `.gitkeep` files through the missing-only file-content map.
- Turned the full Phase 2 validation suite green, including clean-repo init, nested git-root targeting, dry-run, idempotency, raw policy, source exclusions, and git status visibility.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add inspectable `.llm-wiki/` Markdown templates** - `38a5245` (feat)
2. **Task 2: Wire template loading and README/AGENTS-only repo overview seeding** - `d3ddc54` (feat)

**Plan metadata:** committed separately after this summary.

## Files Created/Modified

- `skills/project-llm-wiki/assets/templates/llm-wiki/README.md` - Default wiki purpose, boundaries, and example links.
- `skills/project-llm-wiki/assets/templates/llm-wiki/AGENTS.md` - Agent-facing wiki usage and safety rules.
- `skills/project-llm-wiki/assets/templates/llm-wiki/index.md` - Required navigation links, category headings, and raw-source pointers.
- `skills/project-llm-wiki/assets/templates/llm-wiki/log.md` - Durable wiki log guidance.
- `skills/project-llm-wiki/assets/templates/llm-wiki/raw/README.md` - Strict raw source allow/deny policy.
- `skills/project-llm-wiki/assets/templates/llm-wiki/raw/curated/README.md` - De-secreted curated raw source requirements and example filename.
- `skills/project-llm-wiki/assets/templates/llm-wiki/features/ideas.md` - Durable ideas page with the required idea fields.
- `skills/project-llm-wiki/assets/templates/README.md` - Template inventory and preserved safety rules.
- `skills/project-llm-wiki/scripts/project_wiki.py` - Template loading, repo overview generation, generated content map, and source-status output.
- `skills/project-llm-wiki/tests/test_project_wiki_package.py` - Updated package test to assert the Phase 2 template inventory instead of obsolete Phase 1 deferral wording.

## Decisions Made

- Kept `repo-overview.md` provenance-only. Init checks whether `README.md` and `AGENTS.md` exist but does not read or summarize their contents.
- Kept `.gitkeep` placeholders generated in code, because they are empty operational placeholders rather than meaningful inspectable Markdown templates.
- Kept future manifest-derived tech-stack facts out of the seed page. Agents should inspect current repo files directly when they need those facts.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Updated obsolete package template test**
- **Found during:** Task 1 (Add inspectable `.llm-wiki/` Markdown templates)
- **Issue:** `test_project_wiki_package.py` still asserted the Phase 1 deferral sentence after the plan required replacing that README with a Phase 2 inventory.
- **Fix:** Updated the test to assert inventory entries and preserved template safety wording.
- **Files modified:** `skills/project-llm-wiki/tests/test_project_wiki_package.py`
- **Verification:** `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_package.py`
- **Committed in:** `38a5245`

---

**Total deviations:** 1 auto-fixed (1 blocking issue)
**Impact on plan:** The change kept required verification meaningful and did not widen runtime behavior.

## Issues Encountered

- Test runs generated `skills/project-llm-wiki/tests/__pycache__/`; it was removed after verification and not committed.
- The local `node_modules` GSD SDK CLI was absent for `state.load`; the PATH `gsd-sdk` fallback worked.

## Verification

- Task 1 verification passed:
  - `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_package.py`
  - `rg -n "secrets, credentials, auth tokens, private customer data, full logs, database exports, generated dumps" skills/project-llm-wiki/assets/templates/llm-wiki/raw/README.md`
  - `rg -n "\\[\\[summaries/repo-overview\\]\\]|\\[\\[features/ideas\\]\\]" skills/project-llm-wiki/assets/templates/llm-wiki/index.md`
  - `rg -n "de-secreted|intentionally selected|small sources or excerpts|2026-05-13-api-notes.md" skills/project-llm-wiki/assets/templates/llm-wiki/raw/curated/README.md`
  - `test -f` checks passed for all seven required template files.
- Task 2 verification passed:
  - `python3 -m unittest discover -s skills/project-llm-wiki/tests`
  - `rg -n "build_repo_overview|Sources found:|Sources skipped:" skills/project-llm-wiki/scripts/project_wiki.py`
  - `rg -n "assets.*templates.*llm-wiki|load_template_contents|build_repo_overview" skills/project-llm-wiki/scripts/project_wiki.py`
  - `rg -n "README\\.md|AGENTS\\.md" skills/project-llm-wiki/scripts/project_wiki.py`
  - `rg -n -- "package\\.json|pyproject\\.toml|go\\.mod|Cargo\\.toml" skills/project-llm-wiki/scripts/project_wiki.py` returned no matches, satisfying the exclusion gate.
- Plan-level verification passed:
  - `python3 -m unittest discover -s skills/project-llm-wiki/tests` ran 16 tests and exited 0.
  - Required raw policy, index wikilink, ideas page, and seed-source exclusion greps passed.
  - Clean temporary Git repo smoke passed for `project_wiki.py init --dry-run`, including `Would create paths:` and skipped README/AGENTS source status.

## TDD Gate Compliance

Task 2 was the GREEN transition for the Phase 2 RED fixtures created by Plan 02-03. RED fixture commits exist in `f4cb8b8` and `1c10de5`; the GREEN implementation commit is `d3ddc54`.

## Known Stubs

None. The stub scan found no TODO/FIXME/placeholder text or hardcoded empty UI data. Empty `.gitkeep` content is intentional generated repository scaffolding.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 2 is complete from the package validation perspective. Phase 3 can build lint checks on top of the initialized wiki skeleton and raw policy contract.

## Self-Check: PASSED

- Created template file exists: `skills/project-llm-wiki/assets/templates/llm-wiki/README.md`
- Modified init script exists: `skills/project-llm-wiki/scripts/project_wiki.py`
- Task commits found: `38a5245`, `d3ddc54`
- Full package test suite passed after both task commits.
- Unrelated dirty `AGENTS.md` remained unstaged and untouched by plan commits.

---
*Phase: 02-init-and-wiki-templates*
*Completed: 2026-05-12*
