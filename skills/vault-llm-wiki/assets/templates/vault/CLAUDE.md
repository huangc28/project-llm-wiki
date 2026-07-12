# Vault Schema — Claude Operating Instructions

This file defines how Claude Code operates on this Obsidian vault.
Style guide: [[AI Note-Taking Principles]]

## Source of Truth Rule

This vault at `<ABSOLUTE_VAULT_PATH>` is the maintained AI second brain and the primary source of truth for knowledge lookups, prior ingest status, project context, and long-term memory.

When answering questions like "have we ingested this already?", "what do I know about X?", "what did we decide before?", or "what is the current understanding of this topic?", check this vault first.

Use workspace-local memory, chat summaries, or other temporary context only as secondary aids. If they conflict with the vault, prefer the vault unless the user explicitly says otherwise.

---

## Directory Structure

| Directory | Purpose | Add new content? |
|---|---|---|
| `raw/` | Raw sources — unread URLs, clippings, saved articles | Yes (raw sources only) |
| `projects/` | Project second brains — one subfolder per project | Yes |
| `daily_notes/` | Daily notes, YYYY-MM-DD.md | Yes |
| `skills/` | Claude Code skill definitions — one subfolder per skill | Yes |
| `Ideas/` | Idea notes for projects or features | Yes |
| `待辦/` | Todo and task tracking notes | Yes |
| `Excalidraw/` | Visual diagrams | Yes (diagrams only) |
| `memory/` | Auto-memory or scratch system | Agent-managed only |
| `templates/` | Reusable note templates | Templates only |
| Top-level domain folders such as `golang/`, `react/`, `flutter/`, `vim/`, `nodejs/`, `php/`, `rustlang/`, `web/`, `database/`, `networking/`, `systemd/`, `hosting/` | Technology or domain knowledge bases | Yes |
| Root-level `.md` files | Control files or legacy notes | Do not add new root notes casually |

---

## Page Types

| Type | Location | Purpose |
|---|---|---|
| **Overview note** | `projects/<name>/overview.md` or `<domain>/overview.md` | Top-level summary of a project or domain |
| **Concept note** | `projects/<name>/` or `<domain>/` | Deep dive into one concept or decision |
| **Entity note** | `projects/<name>/` or `<domain>/` | Dedicated page for a tool, protocol, person, or named thing reused across pages |
| **Summary note** | `projects/<name>/summaries/` | Source-level summary that links one ingest to all touched pages |
| **Bookmark note** | `raw/<topic>.md` | Unread raw source (immutable until ingested) |
| **Skill note** | `skills/<name>/SKILL.md` | Claude Code skill definition |
| **Daily note** | `daily_notes/YYYY-MM-DD.md` | Daily log, tasks, reflections |

---

## Frontmatter Conventions

```yaml
---
tags: [category/subcategory]
aliases: [alternative names]
source: https://...          # for bookmarks
author: Name                 # for bookmarks
saved: YYYY-MM-DD            # for bookmarks
status: unread|processed|completed  # for bookmarks
created: YYYY-MM-DD          # for wiki pages
note_type: overview|concept|entity|summary|bookmark|skill|daily
derived_from: [[source-page]]  # provenance — what was used to write this
last_reviewed: YYYY-MM-DD    # when this was last verified
canonical: true|false        # is this the authoritative page on this topic?
knowledge_note: [[parent]]   # link to parent overview
---
```

---

## Three Operations

### Ingest
Triggered by: `"Ingest [source]"`, `"Process [bookmark]"`, `"Silent ingest [source]"`, `"Careful ingest [source]"`, or `"Ingest batch [A], [B], [C]"`

1. Read the raw source
2. Discuss 3–5 key takeaways with the user unless the trigger is silent ingest
3. Read `index.md` to identify which existing pages this source touches
4. Update existing pages first — default to 5–10 pages; max 15 only when clearly warranted
   - Use `"Careful ingest"` to cap updates at 1–3 pages when conservative mode is needed
   - Add provenance note on each touched page: `> Updated from: [[source]] YYYY-MM-DD`
   - Flag contradictions with `> [!] Contradiction: this conflicts with [[other-page]] — needs review`
   - Prefer updating existing pages over creating new ones
   - Add explicit `note_type` frontmatter when creating or materially restructuring pages
   - If a concept or entity is reused across 2 or more pages but lacks its own page, create one
5. If the source touches 3 or more pages, create `projects/<domain>/summaries/<source-title>.md`
6. Mark bookmark `status: processed`
7. Append to `log.md`
8. Update `index.md` with any newly created pages

If the index does not surface relevant pages, fall back to a broad vault search before concluding there is no coverage.

### Query
Triggered by: `"What do I know about X?"`, `"Synthesize my notes on Y"`, or `"Connect X and Y"`

1. Read `index.md` first
2. Read the relevant pages
3. Answer with inline `[[wikilink]]` citations
4. Surface contradictions or gaps when they matter
5. Offer to file a valuable synthesis back as a new note
6. Append to `log.md`

### Lint
Triggered by: `"Lint the vault"`, `"Lint the vault structural"`, `"Lint the vault semantic"`, `"Lint the vault full"`, or `"Reindex the vault"`

Structural checks:
- Broken wikilinks
- Orphan pages
- Stale unread bookmarks
- Index gaps

Semantic checks:
- Contradictions across pages
- Missing cross-references
- Pruning candidates
- Stale claims
- Data gaps for concepts/entities that should have their own note

Reindex mode:
- Scan active content directories
- Add missing files to `index.md`
- Append a reindex entry to `log.md`

---

## Key Files

- `AGENTS.md` — Codex entrypoint that points agents to this file
- `index.md` — Catalog of wiki pages; read this first on every query
- `log.md` — Append-only operation log; append after every ingest/query/lint
- `AI Note-Taking Principles.md` — Note style guide
- `projects/vault-llm-wiki/overview.md` — Architecture and rationale for this wiki system
- `projects/vault-llm-wiki/usage.md` — Trigger phrases and day-to-day workflow

---

## Linking Rules

- Always prefer extending existing pages over creating isolated notes
- Use `[[wikilinks]]` to connect related concepts
- Every new page should link to a parent overview or a nearby concept
- Avoid note explosion: several closely related points belong in one useful note, not many tiny notes
