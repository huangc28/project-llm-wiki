# Roadmap: Project LLM Wiki

## Overview

Project LLM Wiki will ship as a reusable skill package that creates and maintains a git-tracked `.llm-wiki/` knowledge layer inside real project repositories. The roadmap starts with the package boundary and deterministic init behavior, then adds lint safety, the compounding query/ingest loop, and finally agent instruction integration plus validation against a real PeasyDeal repo.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [ ] **Phase 1: Skill Package Foundation** - Create the reusable skill package shape, command surface, and no-dependency execution contract.
- [ ] **Phase 2: Init and Wiki Templates** - Implement safe git-root init, idempotent `.llm-wiki/` skeleton creation, and raw source policy templates.
- [ ] **Phase 3: Lint and Safety Checks** - Add deterministic lint checks for structure, safety, freshness, and repo/wiki drift warnings.
- [ ] **Phase 4: Query and Ingest Loop** - Implement repo-local query and curated ingest behavior with wikilink citations, provenance, index updates, and log entries.
- [ ] **Phase 5: Agent Instructions and Real Repo Validation** - Add merge-safe AGENTS integration and validate the pattern against `peasydeal_be`.

## Phase Details

### Phase 1: Skill Package Foundation

**Goal**: Establish the reusable skill package and implementation boundary for Project LLM Wiki.
**Depends on**: Nothing (first phase)
**Requirements**: [SKILL-01, SKILL-02, SKILL-03]
**UI hint**: no
**Success Criteria** (what must be TRUE):
  1. User can inspect a bounded skill package with `SKILL.md`, templates, scripts, references, and tests.
  2. User can see the documented operations and command surface for init, lint, query, ingest, and later promotion.
  3. User can run or inspect the package without installing new third-party dependencies.
  4. Future phases have a stable package location and file ownership boundary.
**Plans**: 2 plans

Plans:
- [x] 01-01: Define package layout, command surface, and source-of-truth location
- [x] 01-02: Scaffold reusable skill files, references, and baseline tests

### Phase 2: Init and Wiki Templates

**Goal**: Implement safe `.llm-wiki/` initialization with idempotent templates and raw source policy.
**Depends on**: Phase 1
**Requirements**: [INIT-01, INIT-02, INIT-03, INIT-04, INIT-05, INIT-06, RAW-01, RAW-02, RAW-03, TEST-01, TEST-02]
**UI hint**: no
**Success Criteria** (what must be TRUE):
  1. User can run init in a clean git repo and see `.llm-wiki/` files in `git status`.
  2. User can rerun init without duplicated sections or overwritten notes.
  3. User can read seeded wiki templates that define durable project knowledge, raw source policy, and repo-code authority.
  4. User receives clear output identifying the git root used for initialization.
  5. Init handles missing common seed files gracefully.
**Plans**: 3 plans

Plans:
- [ ] 02-01: Implement git-root detection and init safety behavior
- [ ] 02-02: Create `.llm-wiki/` templates and seed page generation
- [ ] 02-03: Add clean repo and idempotency fixture tests

### Phase 3: Lint and Safety Checks

**Goal**: Implement deterministic wiki linting so unsafe or stale `.llm-wiki/` content is visible before rollout.
**Depends on**: Phase 2
**Requirements**: [LINT-01, LINT-02, LINT-03, LINT-04, LINT-05, LINT-06, LINT-07, TEST-04, TEST-05]
**UI hint**: no
**Success Criteria** (what must be TRUE):
  1. User can run lint and receive broken wikilink and missing index entry reports.
  2. User can run lint and receive warnings for secret-looking content and oversized raw files.
  3. User can see stale page and likely repo/wiki contradiction warnings where detectable.
  4. Lint output includes file paths, severity, issue type, and remediation guidance.
  5. Fixture tests prove missing index and secret-looking raw file warnings.
**Plans**: 3 plans

Plans:
- [ ] 03-01: Implement wikilink, index coverage, and file size checks
- [ ] 03-02: Implement secret-looking, stale page, and contradiction warning checks
- [ ] 03-03: Add lint fixtures and actionable output formatting

### Phase 4: Query and Ingest Loop

**Goal**: Implement the repo-local compounding wiki loop: query with citations and ingest curated sources into existing pages first.
**Depends on**: Phase 3
**Requirements**: [QUERY-01, QUERY-02, QUERY-03, QUERY-04, INGEST-01, INGEST-02, INGEST-03, INGEST-04, INGEST-05, TEST-03]
**UI hint**: no
**Success Criteria** (what must be TRUE):
  1. User queries read `.llm-wiki/index.md` first and answer with repo-local `[[wikilink]]` citations.
  2. User queries append date, summary, pages consulted, and key insight to `.llm-wiki/log.md`.
  3. User can ingest a curated source while preserving the raw policy and durable/volatile boundary.
  4. Ingest updates existing pages before creating new pages and creates summaries only for cross-cutting sources.
  5. Query fixture proves cited answer output and log append behavior.
**Plans**: 3 plans

Plans:
- [ ] 04-01: Implement query protocol and log append behavior
- [ ] 04-02: Implement curated ingest protocol, provenance, index updates, and summary rules
- [ ] 04-03: Add query/ingest fixtures and boundary tests

### Phase 5: Agent Instructions and Real Repo Validation

**Goal**: Add merge-safe repo `AGENTS.md` integration and validate the complete pattern against `peasydeal_be` before broader rollout.
**Depends on**: Phase 4
**Requirements**: [AGENT-01, AGENT-02, AGENT-03, AGENT-04, AGENT-05, TEST-06, TEST-07]
**UI hint**: no
**Success Criteria** (what must be TRUE):
  1. User can insert a Project LLM Wiki section into repo `AGENTS.md` without overwriting unrelated guidance.
  2. Existing NotebookLM and workflow sections remain unchanged in fixture tests.
  3. Inserted rules tell agents when to read `.llm-wiki/index.md`, when to update `.llm-wiki/`, and that repo code wins over wiki notes.
  4. `peasydeal_be` dry-run validation reports expected changes without destructive edits.
  5. The final rollout report identifies whether the pattern is ready for `peasydeal_web` and `peasydeal-product-miner`.
**Plans**: 3 plans

Plans:
- [ ] 05-01: Implement marker-bounded AGENTS patching and preservation tests
- [ ] 05-02: Validate against `peasydeal_be` with dry-run reporting
- [ ] 05-03: Document rollout checklist and next-repo application rules

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Skill Package Foundation | 0/2 | Not started | - |
| 2. Init and Wiki Templates | 0/3 | Not started | - |
| 3. Lint and Safety Checks | 0/3 | Not started | - |
| 4. Query and Ingest Loop | 0/3 | Not started | - |
| 5. Agent Instructions and Real Repo Validation | 0/3 | Not started | - |
