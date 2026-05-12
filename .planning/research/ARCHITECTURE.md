# Architecture Research

**Domain:** Repo-local LLM wiki skills for coding agents
**Researched:** 2026-05-12
**Confidence:** MEDIUM

## Standard Architecture

### System Overview

```text
User / Agent command
  |
  v
Skill protocol layer
  - project-wiki-init
  - project-wiki-query
  - project-wiki-ingest
  - project-wiki-lint
  |
  v
Deterministic helper scripts
  - git root detection
  - template creation
  - wikilink parsing
  - lint checks
  - AGENTS patching
  |
  v
Target git repository
  - repo code remains source of truth
  - .llm-wiki/ stores durable project knowledge
  - .planning/ stores GSD workflow state
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| Skill entrypoint | Defines triggers, protocol, safety boundaries, and finish checks | `SKILL.md` |
| Template assets | Seed `.llm-wiki/` files consistently | `assets/templates/*.md` |
| Init helper | Detect git root and create missing skeleton files | Python stdlib script |
| Lint helper | Check deterministic health issues | Python stdlib script |
| Query protocol | Read index, relevant pages, synthesize with citations, append log | Skill protocol plus optional helper for page discovery |
| Ingest protocol | Update existing pages first, track provenance, enforce raw policy | Skill protocol plus optional helper checks |
| AGENTS patcher | Insert or update a bounded Project LLM Wiki section | Deterministic marker-aware script |

## Recommended Project Structure

```text
project-llm-wiki/
├── .planning/
│   ├── PROJECT.md
│   ├── REQUIREMENTS.md
│   ├── ROADMAP.md
│   └── research/
├── skills/
│   └── project-llm-wiki/
│       ├── SKILL.md
│       ├── assets/
│       │   └── templates/
│       ├── scripts/
│       │   └── project_wiki.py
│       ├── tests/
│       └── references/
└── README.md
```

For the generated target repo wiki:

```text
.llm-wiki/
├── README.md
├── AGENTS.md
├── index.md
├── log.md
├── raw/
│   ├── README.md
│   └── curated/
├── architecture/
│   ├── overview.md
│   └── module-map.md
├── domain/
├── decisions/
├── operations/
├── features/
└── summaries/
```

### Structure Rationale

- **`skills/project-llm-wiki/`:** Keeps the reusable skill package bounded and installable.
- **`assets/templates/`:** Avoids embedding long templates directly in the skill prompt.
- **`scripts/`:** Gives init and lint deterministic behavior instead of relying only on LLM judgment.
- **`.llm-wiki/`:** Keeps durable project knowledge beside code and visible in git.
- **`.planning/`:** Keeps GSD workflow state separate from durable wiki knowledge.

## Architectural Patterns

### Pattern 1: Structure First, Raw Files Second

**What:** Read `.llm-wiki/index.md` and orientation pages before broad repo search.
**When to use:** Query, onboarding, architecture/debug/product work.
**Trade-offs:** Reduces token waste and repeated rediscovery, but must tolerate stale wiki content by checking repo code when facts matter.

### Pattern 2: Deterministic Guardrails Around LLM Work

**What:** Use scripts for root detection, skeleton creation, lint, and patch idempotency.
**When to use:** Any behavior that should be stable across runs.
**Trade-offs:** Requires maintaining small scripts, but prevents sloppy file edits and repeated sections.

### Pattern 3: Compounding Updates

**What:** Update existing wiki pages before creating new pages.
**When to use:** Ingesting curated sources or promoting validated work.
**Trade-offs:** Requires reading the index first, but prevents isolated notes and improves long-term retrieval.

### Pattern 4: Durable vs Volatile Boundary

**What:** `.llm-wiki/` stores durable knowledge; `.planning/`, Linear, OMX, and PRs store active state.
**When to use:** Every write decision.
**Trade-offs:** Requires discipline, but keeps the wiki from becoming a task log.

## Data Flow

### Init Flow

```text
Command
  -> resolve git root
  -> check existing .llm-wiki/
  -> create missing directories and templates
  -> optionally patch AGENTS.md
  -> run lint/idempotency checks
  -> report created vs existing files
```

### Query Flow

```text
Question
  -> read .llm-wiki/index.md
  -> read relevant pages
  -> fall back to focused repo search if needed
  -> answer with [[wikilink]] citations
  -> append .llm-wiki/log.md
```

### Ingest Flow

```text
Curated source
  -> validate raw policy
  -> read index and candidate pages
  -> update existing pages first
  -> create summary only for cross-cutting sources
  -> update index and log
  -> run lint
```

## Anti-Patterns

### Anti-Pattern 1: Parent Workspace Wiki

**What people do:** Initialize `.llm-wiki/` in a folder that contains multiple repos.
**Why it's wrong:** Project knowledge becomes ambiguous and does not travel with the actual repo.
**Do this instead:** Detect and use the selected git root.

### Anti-Pattern 2: Wiki as Task Tracker

**What people do:** Store todos, sprint progress, execution checkpoints, and workflow state in `.llm-wiki/`.
**Why it's wrong:** The wiki becomes stale and noisy.
**Do this instead:** Keep active state in GSD, Linear, OMX, PRs, or workflow files.

### Anti-Pattern 3: LLM-Only Safety Checks

**What people do:** Rely on the model to notice broken links, secrets, and duplicates.
**Why it's wrong:** These are deterministic checks and should be repeatable.
**Do this instead:** Implement lint helpers and tests.

## Integration Points

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Skill package to target repo | Filesystem plus git root detection | Must not write outside selected repo |
| Target repo to `.llm-wiki/` | Markdown files | Wiki changes should be visible in git |
| Repo `AGENTS.md` to `.llm-wiki/AGENTS.md` | Section pointer and rules | Keep repo-level rules short and wiki-specific rules in `.llm-wiki/AGENTS.md` |
| GSD to `.llm-wiki/` | Promotion after validated work | Do not auto-copy `.planning/` task state |
| Obsidian to repo wiki | Optional manual synthesis | Not part of v1 sync |
| NotebookLM to repo wiki | Optional retrieval support | Not authoritative |

## Sources

- `knowledge-graph/graphify` - structure-first memory pattern
- `projects/vault-llm-wiki/overview` - raw/wiki/schema layer split
- `projects/vault-llm-wiki/summaries/zaid-karpathy-second-brain-agent-memory-2026-04-29` - Markdown vs machine state boundary
- `Obsidian + Claude Code 個人 OS` - folder structure as context-window management
- User-provided project plan

---
*Architecture research for: repo-local LLM wiki skills*
*Researched: 2026-05-12*
