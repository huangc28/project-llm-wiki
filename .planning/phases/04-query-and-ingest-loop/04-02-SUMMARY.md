---
phase: 04-query-and-ingest-loop
plan: 02
subsystem: cli
tags: [markdown, wiki, ingest, provenance, raw-policy]
requires:
  - phase: 04-query-and-ingest-loop
    provides: query log primitives and page normalization from Plan 04-01
provides:
  - curated text/file/URL ingest source normalization
  - compiled-page-first wiki updates with provenance
  - conditional raw curated source preservation
  - index and ingest log updates
affects: [project-wiki-ingest, llm-wiki-raw-policy, query-and-ingest-loop]
tech-stack:
  added: []
  patterns:
    - stdlib-only argparse subcommand behavior
    - provenance lines on touched wiki pages
    - policy-gated raw curated source copies
key-files:
  created:
    - skills/project-llm-wiki/tests/test_project_wiki_ingest.py
  modified:
    - skills/project-llm-wiki/scripts/project_wiki.py
    - skills/project-llm-wiki/SKILL.md
    - skills/project-llm-wiki/references/command-surface.md
key-decisions:
  - "URLs are treated as provenance unless curated text is supplied; no network fetch is required."
  - "Video URLs without curated text return guidance to provide transcript, summary, or curated notes."
  - "Ingest writes concise key ideas to durable pages and preserves raw copies only when requested and policy-safe."
patterns-established:
  - "Existing-page-first ingest: update target pages before creating new pages."
  - "New page guard: require `--new-page-reason` and enforce the 15-page hard cap."
  - "Ingest log entries use `Pages touched` and bounded key ideas."
requirements-completed: [INGEST-01, INGEST-02, INGEST-03, INGEST-04, INGEST-05]
duration: 11min
completed: 2026-05-13
---

# Phase 04 Plan 02: Curated Ingest Protocol Summary

**Curated source ingest with existing-page-first writes, provenance, index updates, raw policy, and ingest logs**

## Performance

- **Duration:** 11 min
- **Started:** 2026-05-13T09:15:00Z
- **Completed:** 2026-05-13T09:26:30Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- Replaced the planned `project-wiki ingest` stub with a real curated source boundary for `--text`, `--file`, and `--url` provenance.
- Added raw policy enforcement for secret-looking text, oversized text, full transcripts/logs/dumps, private data, active task state, and execution checkpoints.
- Implemented durable page updates with provenance, optional new pages with index updates, optional curated raw note preservation, and ingest log entries.
- Documented video preprocessing and the `$watch-video` non-dependency boundary.

## Task Commits

1. **Task 1: Add source normalization and raw policy enforcement** - `2213f1a` (feat)
2. **Task 2: Add existing-page-first writes, provenance, index updates, and ingest log** - `e557363` (feat)
3. **Task 3: Document the adapter-agnostic ingest protocol** - `0e96d35` (docs)

## Files Created/Modified

- `skills/project-llm-wiki/tests/test_project_wiki_ingest.py` - Ingest subprocess fixtures for source handling, raw policy, page writes, provenance, index updates, raw copies, and logs.
- `skills/project-llm-wiki/scripts/project_wiki.py` - Ingest parser, source normalization, page-path validation, page update helpers, index update, raw preservation, and result rendering.
- `skills/project-llm-wiki/SKILL.md` - Ingest protocol, video preprocessing note, existing-page-first rule, raw policy, and 15-page hard cap.
- `skills/project-llm-wiki/references/command-surface.md` - Implemented ingest command examples and safety behavior.

## Decisions Made

- Allowed URL provenance without automatic fetching to avoid SSRF-like behavior and dependency creep.
- Kept video support adapter-agnostic; core ingest asks for curated text when no adapter output is available.
- Made raw curated copies opt-in with `--preserve-raw`, keeping compiled wiki pages as the primary durable layer.

## Deviations from Plan

None - plan executed exactly as written.

---

**Total deviations:** 0 auto-fixed.
**Impact on plan:** No scope changes.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests -p "test_project_wiki_ingest.py"` - 14 tests passed.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests -p "test_project_wiki_package.py"` - 11 tests passed.
- `python3 -m unittest discover -s skills/project-llm-wiki/tests` - 100 tests passed.
- `python3 skills/project-llm-wiki/scripts/project_wiki.py ingest --help` - exits 0 and shows Phase 4 ingest flags.

## Self-Check: PASSED

- `project-wiki ingest` no longer returns the planned Phase 4 stub.
- Text, file, and URL-provenance curated source inputs are accepted.
- Video URL without curated text asks for transcript, summary, or curated notes.
- Existing pages are updated before new pages, and new pages require an explicit reason.
- Touched pages receive provenance, new pages update `index.md`, and ingest appends `log.md`.
- Unsafe raw material and active task state are rejected.

## Next Phase Readiness

Plan 04-03 can harden seeded query/ingest fixture coverage, package help assertions, command-surface docs, and Phase 4 testing references.

---
*Phase: 04-query-and-ingest-loop*
*Completed: 2026-05-13*
