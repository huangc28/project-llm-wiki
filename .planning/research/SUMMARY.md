# Project Research Summary

**Project:** Project LLM Wiki
**Domain:** Repo-local LLM wiki skills for coding agents
**Researched:** 2026-05-12
**Confidence:** MEDIUM

## Executive Summary

Project LLM Wiki should adapt the Karpathy/vault LLM Wiki loop into a repo-local, git-tracked knowledge layer. The central product is not a general notes app; it is a reusable skill package that creates and maintains `.llm-wiki/` inside the actual git repo so future agents can recover durable project context from code-adjacent Markdown.

The recommended v1 approach is intentionally small: Markdown skill definitions, templates, and Python standard-library helper scripts. Init and lint should be deterministic because they touch real repositories and enforce safety boundaries. Query and ingest can remain more LLM-guided, but must read `index.md` first, cite `[[wikilinks]]`, append `log.md`, and update existing pages before creating new ones.

The main risk is boundary collapse: the wiki can accidentally become a task tracker, secret dump, stale source of truth, or parent-workspace notebook. The roadmap should therefore start with git-root detection, idempotent init, raw-source policy, structural lint, and clean fixture tests before adding richer ingest/query/promotion flows.

## Key Findings

### Recommended Stack

Use Markdown-first skill packaging plus deterministic helper scripts.

**Core technologies:**
- Markdown `SKILL.md`: trigger and protocol surface, matching existing skill practice.
- Python 3 standard library: deterministic init, lint, wikilink parsing, and AGENTS patching without new dependencies.
- Git: repo root detection and reviewable `.llm-wiki/` changes.
- `.llm-wiki/`: durable project knowledge layer, separate from `.planning/`.

### Expected Features

**Must have (table stakes):**
- Git-root detection - prevents multi-repo workspace mistakes.
- Idempotent init - safe reruns without overwriting notes.
- Core templates - `README.md`, `AGENTS.md`, `index.md`, `log.md`, `raw/README.md`.
- Raw source policy - keeps secrets and noisy dumps out of git.
- Structural lint - broken links, index gaps, stale pages, secret-looking content, oversized raw files.

**Should have (competitive):**
- Query protocol with wikilink citations and log append.
- Ingest protocol that updates existing pages first.
- Merge-safe AGENTS patching that preserves NotebookLM sections.
- Promotion workflow for validated GSD/PR/debug learnings.

**Defer (v2+):**
- Automatic Obsidian sync.
- NotebookLM export or sync.
- Vector database or graph artifact layer.

### Architecture Approach

Build a bounded reusable skill package with `SKILL.md`, `assets/templates/`, `scripts/`, and tests. The skill operates on a target git repository, creates `.llm-wiki/`, and keeps volatile workflow artifacts in `.planning/`, Linear, OMX, or PR state.

**Major components:**
1. Skill protocol - user-facing triggers and safety rules.
2. Template assets - stable initial wiki files.
3. Deterministic scripts - init, lint, and AGENTS patch safety.
4. Target repo wiki - durable Markdown knowledge under `.llm-wiki/`.

### Critical Pitfalls

1. **Wrong target directory** - avoid by resolving and reporting git root.
2. **Wiki becomes task log** - avoid by enforcing durable vs volatile boundaries.
3. **Unsafe raw sources** - avoid with raw policy and lint patterns.
4. **AGENTS clobbering** - avoid with marker-bounded patching and fixtures.
5. **Stale wiki overrides code** - avoid by stating repo code wins and linting stale claims.

## Implications for Roadmap

### Phase 1: Init and Lint MVP

**Rationale:** This proves the safety boundary and creates the repo-local knowledge substrate.
**Delivers:** Reusable skill package skeleton, init command, core `.llm-wiki/` templates, deterministic lint checks, clean test repo validation.
**Addresses:** Git-root detection, idempotency, raw policy, structural lint.
**Avoids:** Wrong directory wiki, unsafe raw source tracking, wiki as task log.

### Phase 2: Query, Ingest, and AGENTS Integration

**Rationale:** Once the skeleton is safe, add compounding behavior and agent routing.
**Delivers:** Query protocol, ingest protocol, merge-safe AGENTS patching, NotebookLM preservation fixture.
**Uses:** Index/log templates and deterministic patch helpers.
**Implements:** The core Karpathy/vault loop in repo-local form.

### Phase 3: Promotion and Real Repo Rollout

**Rationale:** After core behaviors are proven in fixtures, validate against `peasydeal_be`.
**Delivers:** Promotion workflow for validated work, rollout checklist, real repo dry run, lint report.
**Implements:** Durable handoff from GSD/PR/debug learnings into `.llm-wiki/`.

### Phase 4: Optional Bridges and Hardening

**Rationale:** Only after the repo-local loop works should adjacent systems be connected.
**Delivers:** Optional Obsidian summary guidance, NotebookLM retrieval guidance, advanced stale/contradiction lint, packaging polish.

### Phase Ordering Rationale

- Init and lint come first because they prevent unsafe writes and wrong-repo rollout.
- Query and ingest depend on a stable index/log structure.
- AGENTS patching should wait until templates and wiki rules stabilize.
- Promotion depends on a clear durable/volatile boundary.
- Obsidian and NotebookLM bridges should not be built until the repo-local source-of-truth pattern is validated.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 1:** Exact skill package location and install strategy.
- **Phase 2:** Marker strategy for merge-safe AGENTS patching.
- **Phase 3:** `peasydeal_be` current NotebookLM/AGENTS instructions.

Phases with standard patterns:
- **Phase 1:** Markdown templates, git-root detection, and deterministic lint use established local patterns.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | Strong local skill patterns, but final package location still needs a decision |
| Features | HIGH | Directly derived from user plan and vault LLM Wiki operations |
| Architecture | MEDIUM | Clear direction, implementation details should follow existing repo and skill conventions |
| Pitfalls | HIGH | Risks are explicit in the user plan and vault notes |

**Overall confidence:** MEDIUM

### Gaps to Address

- **Install strategy:** Decide whether this repo is the skill source of truth or whether it mirrors a vault-managed skill.
- **Command surface:** Decide whether to expose one `project-llm-wiki` skill with modes or separate `project-wiki-*` skills.
- **AGENTS patch markers:** Define exact markers and fixture tests.
- **PeasyDeal rollout:** Inspect `peasydeal_be` before real patching.

## Sources

### Primary (HIGH confidence)

- User-provided Git-Tracked Project LLM Wiki plan - scope, structure, mechanisms, rollout, test plan.
- `projects/vault-llm-wiki/overview` - Karpathy LLM Wiki adaptation.
- `projects/vault-llm-wiki/usage` - day-to-day ingest/query/lint loop.
- `skills/vault-ingest/SKILL` - compounding ingest protocol.
- `skills/vault-query/SKILL` - query protocol.
- `skills/vault-lint/SKILL` - lint protocol.

### Secondary (MEDIUM confidence)

- `skills/README` - local skill packaging conventions.
- `knowledge-graph/graphify` - structure-first memory pattern.
- `Obsidian vs NotebookLM 分水嶺` - boundary between repo, NotebookLM, and Obsidian.
- `projects/vault-llm-wiki/summaries/zaid-karpathy-second-brain-agent-memory-2026-04-29` - Markdown versus machine memory split.

---
*Research completed: 2026-05-12*
*Ready for roadmap: yes*
