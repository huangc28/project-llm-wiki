# Requirements: Project LLM Wiki

**Defined:** 2026-05-12
**Core Value:** Future agents and contributors can recover durable project context from the repository itself without confusing curated project knowledge with volatile task state.

## v1 Requirements

Requirements for the initial reusable skill release. Each maps to roadmap phases.

### Skill Package

- [x] **SKILL-01**: User can install or reference a reusable Project LLM Wiki skill package with documented project wiki operations.
- [x] **SKILL-02**: User can run the skill safely from inside a git repository without requiring external runtime dependencies beyond the selected standard-library implementation.
- [x] **SKILL-03**: User can inspect templates, scripts, and references in the skill package without reading a single large monolithic prompt.

### Initialization

- [x] **INIT-01**: User can initialize `.llm-wiki/` in the actual git root detected by `git rev-parse --show-toplevel`.
- [x] **INIT-02**: User receives a clear failure or target-selection message when running init outside a git repository or from a multi-repo parent that is not the intended repo.
- [x] **INIT-03**: User can initialize a missing `.llm-wiki/` skeleton with `README.md`, `AGENTS.md`, `index.md`, `log.md`, `raw/README.md`, `raw/curated/`, `architecture/`, `domain/`, `decisions/`, `operations/`, `features/`, and `summaries/`.
- [x] **INIT-04**: User can rerun init without overwriting existing wiki notes or duplicating generated sections.
- [x] **INIT-05**: User can seed concise starting pages from existing repo files such as `README.md`, package manifests, `go.mod`, `pyproject.toml`, and `AGENTS.md` when those files exist.
- [ ] **INIT-06**: User can see `.llm-wiki/` files in `git status` after init unless the target repo already ignores them.

### Raw Source Policy

- [x] **RAW-01**: User can read `.llm-wiki/raw/README.md` to understand what raw sources are allowed and disallowed.
- [x] **RAW-02**: User is warned not to store secrets, credentials, private customer data, auth tokens, full logs, database exports, or generated large dumps in `.llm-wiki/`.
- [x] **RAW-03**: User can store only curated, de-secreted project sources under `.llm-wiki/raw/curated/`.

### Query

- [ ] **QUERY-01**: User can query project wiki knowledge and the skill reads `.llm-wiki/index.md` before reading individual wiki pages.
- [ ] **QUERY-02**: User receives answers that cite repo-local wiki pages with `[[wikilink]]` citations.
- [ ] **QUERY-03**: User receives a clear "not covered" answer when `.llm-wiki/` has no relevant coverage, with a suggestion to ingest or initialize relevant pages.
- [ ] **QUERY-04**: User queries append an entry to `.llm-wiki/log.md` with date, query summary, pages consulted, and key insight.

### Ingest

- [ ] **INGEST-01**: User can ingest a curated project source into `.llm-wiki/` without storing unsafe raw material.
- [ ] **INGEST-02**: Ingest updates existing wiki pages before creating new pages.
- [ ] **INGEST-03**: Ingest creates a summary page only when a source affects multiple wiki areas or cross-cutting project knowledge.
- [ ] **INGEST-04**: Ingest adds provenance to touched pages and updates `.llm-wiki/index.md` and `.llm-wiki/log.md`.
- [ ] **INGEST-05**: Ingest keeps active task state, execution checkpoints, and unvalidated work out of `.llm-wiki/`.

### Lint

- [ ] **LINT-01**: User can run a structural lint that detects broken wikilinks.
- [ ] **LINT-02**: User can run a structural lint that detects files missing from `.llm-wiki/index.md`.
- [ ] **LINT-03**: User can run a safety lint that detects secret-looking content in `.llm-wiki/raw/` and other wiki files.
- [ ] **LINT-04**: User can run a size lint that detects oversized raw files or generated dump-like files.
- [ ] **LINT-05**: User can run a freshness lint that flags stale wiki pages needing review.
- [ ] **LINT-06**: User can receive likely repo/wiki contradiction warnings when wiki claims appear to disagree with current repo files.
- [ ] **LINT-07**: Lint output includes file paths, issue type, severity, and actionable remediation guidance.

### Agent Instructions

- [ ] **AGENT-01**: User can add a short Project LLM Wiki section to repo `AGENTS.md` without overwriting unrelated agent instructions.
- [ ] **AGENT-02**: AGENTS patching preserves existing NotebookLM sections and workflow-specific guidance.
- [ ] **AGENT-03**: The inserted Project LLM Wiki rules tell agents to read `.llm-wiki/index.md` before non-trivial architecture, debugging, product, or onboarding work.
- [ ] **AGENT-04**: The inserted rules state that current repo code is authoritative when it disagrees with `.llm-wiki/`.
- [ ] **AGENT-05**: The inserted rules tell agents to update `.llm-wiki/` only after validated non-trivial work and never use it for task status.

### Validation

- [ ] **TEST-01**: A clean test repo can run init and show `.llm-wiki/` files in `git status`.
- [ ] **TEST-02**: A clean test repo can rerun init without duplicated sections or overwritten notes.
- [ ] **TEST-03**: Query against seeded pages returns wiki-cited answers and appends `.llm-wiki/log.md`.
- [ ] **TEST-04**: Lint with an intentionally missing index entry reports the issue.
- [ ] **TEST-05**: Lint with an intentionally secret-looking raw file reports the issue.
- [ ] **TEST-06**: AGENTS patching against a fixture with an existing NotebookLM section preserves that section.
- [ ] **TEST-07**: The pattern is dry-run validated against `peasydeal_be` before being applied to other PeasyDeal repos.

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Promotion

- **PROM-01**: User can promote validated GSD, PR, debug, or incident learnings into `.llm-wiki/` without copying volatile task state.
- **PROM-02**: User can require human confirmation before promotion touches high-value architecture or decision pages.

### Cross-System Bridges

- **BRIDGE-01**: User can optionally export or summarize selected `.llm-wiki/` pages back into Obsidian for cross-project synthesis.
- **BRIDGE-02**: User can optionally prepare NotebookLM-friendly curated source material without making NotebookLM the source of truth.
- **BRIDGE-03**: User can optionally generate graph-oriented artifacts after the Markdown wiki workflow is validated.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Store active task state in `.llm-wiki/` | GSD, Linear, OMX, PRs, and workflow files already own active state |
| Store secrets, credentials, private customer data, full logs, database exports, or generated large dumps | Unsafe for git-tracked project knowledge |
| Replace Obsidian | Obsidian remains the cross-project personal synthesis layer |
| Replace NotebookLM | NotebookLM remains an optional retrieval and Q&A layer |
| Add a vector database in v1 | Too much operational weight before proving the Markdown workflow |
| Automatically rewrite existing AGENTS.md content | High risk of clobbering repo-specific instructions |
| Initialize `.llm-wiki/` in a multi-repo parent by default | Project knowledge must live inside the actual git repo |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SKILL-01 | Phase 1 | Complete |
| SKILL-02 | Phase 1 | Complete |
| SKILL-03 | Phase 1 | Complete |
| INIT-01 | Phase 2 | Complete |
| INIT-02 | Phase 2 | Complete |
| INIT-03 | Phase 2 | Complete |
| INIT-04 | Phase 2 | Complete |
| INIT-05 | Phase 2 | Complete |
| INIT-06 | Phase 2 | Pending |
| RAW-01 | Phase 2 | Complete |
| RAW-02 | Phase 2 | Complete |
| RAW-03 | Phase 2 | Complete |
| QUERY-01 | Phase 4 | Pending |
| QUERY-02 | Phase 4 | Pending |
| QUERY-03 | Phase 4 | Pending |
| QUERY-04 | Phase 4 | Pending |
| INGEST-01 | Phase 4 | Pending |
| INGEST-02 | Phase 4 | Pending |
| INGEST-03 | Phase 4 | Pending |
| INGEST-04 | Phase 4 | Pending |
| INGEST-05 | Phase 4 | Pending |
| LINT-01 | Phase 3 | Pending |
| LINT-02 | Phase 3 | Pending |
| LINT-03 | Phase 3 | Pending |
| LINT-04 | Phase 3 | Pending |
| LINT-05 | Phase 3 | Pending |
| LINT-06 | Phase 3 | Pending |
| LINT-07 | Phase 3 | Pending |
| AGENT-01 | Phase 5 | Pending |
| AGENT-02 | Phase 5 | Pending |
| AGENT-03 | Phase 5 | Pending |
| AGENT-04 | Phase 5 | Pending |
| AGENT-05 | Phase 5 | Pending |
| TEST-01 | Phase 2 | Pending |
| TEST-02 | Phase 2 | Pending |
| TEST-03 | Phase 4 | Pending |
| TEST-04 | Phase 3 | Pending |
| TEST-05 | Phase 3 | Pending |
| TEST-06 | Phase 5 | Pending |
| TEST-07 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 40 total
- Mapped to phases: 40
- Unmapped: 0

---
*Requirements defined: 2026-05-12*
*Last updated: 2026-05-12 after roadmap creation*
