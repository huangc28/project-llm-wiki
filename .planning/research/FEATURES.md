# Feature Research

**Domain:** Repo-local LLM wiki skills for coding agents
**Researched:** 2026-05-12
**Confidence:** HIGH

## Feature Landscape

### Table Stakes (Users Expect These)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Git-root detection | Multi-repo workspaces must initialize the wiki in the real repo | LOW | Use `git rev-parse --show-toplevel`; fail clearly outside git |
| Idempotent `.llm-wiki/` skeleton creation | Init must be safe to rerun | MEDIUM | Never overwrite existing notes; append only bounded sections |
| Core templates | A wiki without `README.md`, `index.md`, `log.md`, and raw policy is not usable | LOW | Keep templates concise and repo-oriented |
| Raw source policy | Users need a clear safety boundary for what can be tracked | LOW | Explicitly ban secrets, credentials, private customer data, full logs, dumps |
| Query protocol | Future agents need a repeatable way to read the wiki | MEDIUM | Read `index.md` first, cite `[[wikilinks]]`, append `log.md` |
| Lint protocol | The wiki needs health checks to stay trustworthy | MEDIUM | Broken links, missing index entries, stale pages, secret-looking content |
| AGENTS.md rules | Agents need to know when to read and update `.llm-wiki/` | MEDIUM | Patch merge-safely and do not clobber existing NotebookLM content |

### Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Project/wiki contradiction detection | Keeps repo code authoritative over stale notes | HIGH | Start with likely contradiction heuristics; deeper semantic checks later |
| Promote validated work into wiki | Makes GSD/PR/debug learnings durable without copying task state | MEDIUM | Add after init/lint/query stabilize |
| De-secreted curated raw source handling | Allows provenance without unsafe dumps | MEDIUM | Store only curated excerpts and summaries |
| Multi-repo rollout guardrails | Prevents accidental parent workspace wiki creation | LOW | Important for PeasyDeal workspace shape |
| Obsidian/NotebookLM bridge guidance | Clarifies how adjacent systems should relate | LOW | Document boundaries rather than syncing automatically in v1 |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Auto-ingest everything | Seems convenient | Creates secrets, stale content, and noisy wiki pages | Curated ingest with raw policy and lint |
| Store active task status in `.llm-wiki/` | Looks like a complete project memory | Duplicates GSD, Linear, OMX, and PR state | Keep task state in `.planning/`, Linear, OMX, or workflow files |
| Replace Obsidian with repo wiki | Reduces tools | Loses cross-project synthesis and personal methodology layer | Use repo wiki for project-local durable knowledge |
| Replace NotebookLM with repo wiki | Simplifies retrieval story | NotebookLM remains useful for Q&A over larger curated corpora | Keep NotebookLM optional and non-authoritative |
| Add vector DB in v1 | Sounds agentic | Adds maintenance before proving Markdown workflow value | Start with files, index, and deterministic lint |

## Feature Dependencies

```text
Git-root detection
  requires -> Init skeleton
    requires -> Templates and raw policy
      enables -> Query protocol
      enables -> Lint protocol
      enables -> AGENTS.md patching

Lint protocol
  enhances -> Init safety
  enables -> Rollout validation

Query protocol
  requires -> Index and log
  enhances -> Future agent onboarding

Promote validated work
  requires -> Stable wiki schema
  requires -> Query and lint protocols
```

### Dependency Notes

- **Init requires git-root detection:** Without this, multi-repo workspaces can put `.llm-wiki/` in the wrong place.
- **Query requires index and log:** The wiki needs both navigation and operational history.
- **Lint enables rollout:** Safety checks are needed before applying the pattern to `peasydeal_be`.
- **Promote requires schema stability:** Promotion should come after the durable/volatile boundary is proven.

## MVP Definition

### Launch With (v1)

- [ ] `project-wiki-init` - create the skeleton safely and idempotently.
- [ ] Core `.llm-wiki/` templates - `README.md`, `AGENTS.md`, `index.md`, `log.md`, `raw/README.md`.
- [ ] `project-wiki-lint` structural checks - broken links, missing index entries, secret-looking content, oversized raw files.
- [ ] Clean test repo validation - prove files are git-visible and init is idempotent.
- [ ] `peasydeal_be` dry rollout plan - verify AGENTS patching does not overwrite NotebookLM guidance.

### Add After Validation (v1.x)

- [ ] `project-wiki-query` - answer from `.llm-wiki/` with wikilink citations and query logging.
- [ ] `project-wiki-ingest` - update existing pages first and create summaries only when cross-cutting.
- [ ] AGENTS patch command - marker-bounded section insertion with idempotency tests.

### Future Consideration (v2+)

- [ ] `project-wiki-promote` - promote validated GSD/PR/debug learnings into `.llm-wiki/`.
- [ ] Optional Obsidian sync - only for cross-project synthesis, not as source of truth.
- [ ] Optional NotebookLM export guidance - only for retrieval layer support.
- [ ] Optional graph artifact support - only after Markdown workflow proves useful.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Git-root detection | HIGH | LOW | P1 |
| Idempotent init | HIGH | MEDIUM | P1 |
| Core templates | HIGH | LOW | P1 |
| Raw source policy | HIGH | LOW | P1 |
| Structural lint | HIGH | MEDIUM | P1 |
| Clean test repo validation | HIGH | LOW | P1 |
| Query protocol | MEDIUM | MEDIUM | P2 |
| Ingest protocol | MEDIUM | MEDIUM | P2 |
| AGENTS patching | MEDIUM | MEDIUM | P2 |
| Promote validated work | MEDIUM | MEDIUM | P3 |
| Obsidian sync | LOW | HIGH | P3 |

## Sources

- User-provided Git-Tracked Project LLM Wiki plan
- `projects/vault-llm-wiki/overview`
- `projects/vault-llm-wiki/usage`
- `projects/vault-llm-wiki/knowledge-to-skills-to-routines`
- `skills/vault-ingest/SKILL`
- `skills/vault-query/SKILL`
- `skills/vault-lint/SKILL`

---
*Feature research for: repo-local LLM wiki skills*
*Researched: 2026-05-12*
