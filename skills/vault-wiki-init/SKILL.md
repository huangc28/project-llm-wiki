---
name: vault-wiki-init
description: Bootstrap the current compounding LLM wiki architecture into an Obsidian vault. Use when the user says "vault wiki init" or wants Claude Code to install vault control files, a Codex/Claude entrypoint, companion skills, wiki-system project notes, an initial index, and an append-only log without silently overwriting existing files.
---

# Vault Wiki Init

Bootstrap the current compounding LLM wiki workflow into any Obsidian vault. This skill installs:

- a root `AGENTS.md` that points Codex-class agents to `CLAUDE.md`
- a root `CLAUDE.md` with the vault schema and operating contract
- `AI Note-Taking Principles.md`
- `projects/vault-llm-wiki/overview.md`
- `projects/vault-llm-wiki/usage.md`
- three companion skills: `vault-ingest`, `vault-query`, `vault-lint`
- a seeded `index.md`
- an append-only `log.md`

The bootstrap is conservative. It never silently overwrites an existing target file.

## Trigger

- `vault wiki init`

## Operating Rules

- Plain Claude Code only. Do not rely on OMC, npm, external packages, or vault-specific MCP tools.
- Use normal filesystem operations and basic shell commands only.
- Ask the Step 1 question exactly as written.
- Treat all paths as absolute filesystem paths.
- Use today's date in `YYYY-MM-DD` format.
- Never silently overwrite any target file created by this bootstrap.
- If the user declines backup in Step 3, stop without changing existing target files.
- If any required backup target already exists, stop and report the conflict instead of overwriting it.
- Write embedded file contents exactly where this skill says "exact".
- When generating `index.md` and `log.md`, follow the templates and substitution rules in this skill.

## Protocol

### Step 1: Ask for vault path

Ask exactly:

`What is the absolute path to your Obsidian vault? (e.g. /Users/yourname/Documents/notes)`

Wait for the user's answer before doing anything else.

### Step 2: Validate

Validate that the provided path exists and is a directory.

- If it does not exist, respond with:
  `Error: vault path does not exist: <path>`
- If it exists but is not a directory, respond with:
  `Error: path is not a directory: <path>`

Do not continue on invalid input.

### Step 3: Protect existing files

Check whether any of these target files already exist:

- `<vault>/AGENTS.md`
- `<vault>/CLAUDE.md`
- `<vault>/AI Note-Taking Principles.md`
- `<vault>/index.md`
- `<vault>/log.md`
- `<vault>/projects/vault-llm-wiki/overview.md`
- `<vault>/projects/vault-llm-wiki/usage.md`
- `<vault>/skills/vault-ingest/SKILL.md`
- `<vault>/skills/vault-query/SKILL.md`
- `<vault>/skills/vault-lint/SKILL.md`

If none exist, continue to Step 4.

If any exist, list only the ones found and ask exactly:

`Found existing [files]. Back them up as .bak before proceeding? (yes/no)`

Behavior:

- If the user answers `yes`, rename each found file in place by appending `.bak`.
- If any destination `.bak` file already exists, stop and report the conflict instead of overwriting it.
- If the user answers `no`, stop and explain that the bootstrap was aborted to avoid overwriting existing files.

### Step 4: Create directory structure

Create these directories if they do not already exist:

- `<vault>/raw/`
- `<vault>/projects/`
- `<vault>/projects/vault-llm-wiki/`
- `<vault>/daily_notes/`
- `<vault>/skills/`
- `<vault>/skills/vault-ingest/`
- `<vault>/skills/vault-query/`
- `<vault>/skills/vault-lint/`
- `<vault>/Ideas/`

Track which directories were newly created so they can be reported later.

### Step 5: Write `AGENTS.md`

Write `<vault>/AGENTS.md` exactly as shown.

File: `AGENTS.md`

````markdown
# Agent Instructions

**CRITICAL: All vault-specific operating instructions are in [[CLAUDE.md]]. Read that file before performing any file operations in this vault.**

This vault at `<ABSOLUTE_VAULT_PATH>` is the maintained AI second brain and the primary source of truth for knowledge lookups, prior ingest status, project context, and long-term memory.

When answering questions like "have we ingested this already?", "what do I know about X?", "what did we decide before?", or "what is the current understanding of this topic?", check this vault first.

Use workspace-local memory, chat summaries, or other temporary context only as secondary aids. If they conflict with the vault, prefer the vault unless the user explicitly says otherwise.

See [[CLAUDE.md]] for the full vault schema, directory map, page types, frontmatter conventions, and ingest/query/lint protocols.
````

Replace `<ABSOLUTE_VAULT_PATH>` with the provided vault path.

### Step 6: Write `CLAUDE.md`

Write `<vault>/CLAUDE.md` exactly as shown.

File: `CLAUDE.md`

````markdown
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
````

Replace `<ABSOLUTE_VAULT_PATH>` with the provided vault path.

### Step 7: Write `AI Note-Taking Principles.md`

Write `<vault>/AI Note-Taking Principles.md` exactly as shown.

File: `AI Note-Taking Principles.md`

````markdown
---
aliases:
  - ai note taking rules
  - ai knowledge capture rules
tags:
  - ai/agent
  - note-taking
  - learning/mindmap
---

# AI Note-Taking Principles

This note defines the default way AI discussions should be captured in this vault.

## Default rule

Record AI discussions as a mind-map-style knowledge structure, not as long linear summaries.

## Core principles

- Start from a parent note for the topic.
- Break the topic into smaller concept notes when needed.
- Use wikilinks to connect parent topics, subtopics, and related ideas.
- Prefer clear knowledge points over long paragraphs.
- Keep only high-signal ideas, decisions, frameworks, and open questions.
- Do not create a separate note for every minor point.
- Expand the note network gradually instead of over-structuring too early.

## Preferred note structure

1. Create or update one overview note.
2. Identify 3 to 6 major subtopics.
3. Create child notes only for important subtopics.
4. Link the notes with wikilinks.
5. Capture open questions and next areas to explore.

## What to capture

- Core concepts and main arguments
- Relationships between ideas
- Key distinctions and decisions
- Open questions and follow-up topics

## What to avoid

- Low-signal chat transcript dumps
- Repetitive summaries
- Note explosion from over-splitting
- Decorative structure without real insight

## Working rule for future AI agents

When helping with note-taking in this vault:
- First look for an existing parent note
- Extend the existing note network before creating new scattered notes
- Organize ideas as concept nodes and links
- Prefer concise, readable notes
- Keep the structure useful for later review and learning
````

### Step 8: Write wiki-system project notes

Write these files exactly.

File: `projects/vault-llm-wiki/overview.md`

````markdown
---
tags: [vault/meta, workflow/ai-agent, methodology/llm-wiki]
aliases: [llm wiki plan, vault compounding plan]
created: <TODAY>
status: active
note_type: overview
canonical: true
---

# Vault LLM Wiki — Overview

This note explains the knowledge-system architecture installed by `vault wiki init`.

## Core idea

Use a compounding wiki instead of ad-hoc note creation. New sources should usually make existing notes richer before they create new notes.

## Three layers

| Layer | Meaning in this vault |
|---|---|
| Raw sources | `raw/` bookmarks, clips, saved articles, PDFs, videos |
| The wiki | `projects/`, domain folders, and `skills/` notes that store curated knowledge |
| The schema | `AGENTS.md`, `CLAUDE.md`, `index.md`, `log.md`, and the companion skills |

## Installed workflow surfaces

- `AGENTS.md` tells Codex-class agents to read `CLAUDE.md`
- `CLAUDE.md` defines how agents should operate in the vault
- `skills/vault-ingest/SKILL.md` handles compounding ingest
- `skills/vault-query/SKILL.md` handles synthesis queries
- `skills/vault-lint/SKILL.md` handles reindexing and health checks
- `index.md` is the orientation map
- `log.md` is the append-only operation history

## Operating principle

- Before: new source -> isolated new note
- After: new source -> existing notes get richer, then new notes are created only when needed

## Verification signals

- A query like "What do I know about X?" resolves through `index.md`
- An ingest updates existing notes, marks bookmarks as processed, and appends `log.md`
- A lint pass can identify broken links, orphans, stale claims, and data gaps
````

File: `projects/vault-llm-wiki/usage.md`

````markdown
---
tags: [vault/meta, workflow/ai-agent]
aliases: [llm wiki usage, vault workflow guide]
created: <TODAY>
note_type: concept
---

# Vault LLM Wiki — Usage Guide

How to use the compounding vault system day to day.

## Ingest

Triggers:
- `"Ingest [URL or title]"`
- `"Silent ingest [URL or title]"`
- `"Careful ingest [URL or title]"`
- `"Ingest batch [A], [B], [C]"`
- `"Daily digest"`

Expected behavior:
- read the source
- inspect `index.md`
- update 5 to 10 existing pages by default
- create new concept/entity/summary pages only when warranted
- append to `log.md`

## Query

Triggers:
- `"What do I know about X?"`
- `"Synthesize my notes on Y"`
- `"Connect X and Y"`

Expected behavior:
- read `index.md` first
- cite the vault with `[[wikilinks]]`
- surface contradictions or missing coverage
- optionally file the synthesis back into the wiki

## Lint and reindex

Triggers:
- `"Lint the vault"`
- `"Lint the vault structural"`
- `"Lint the vault semantic"`
- `"Lint the vault full"`
- `"Reindex the vault"`

Expected behavior:
- structural lint checks links, orphans, stale bookmarks, and index gaps
- semantic lint checks contradictions, missing cross-links, stale claims, and data gaps
- reindex adds missing entries to `index.md`
````

Replace `<TODAY>` with today's date.

### Step 9: Write companion skills

Write these files exactly.

File: `skills/vault-ingest/SKILL.md`

````markdown
---
name: vault-ingest
description: Ingest a raw source into the Obsidian vault wiki. Use when the user wants to ingest or process a bookmark, URL, file, or source into existing vault notes with compounding updates.
---

# vault-ingest

Ingest a raw source into the vault wiki. Update existing pages first; do not default to isolated new notes.

## Trigger

- `"Ingest [URL or file]"` or `"Process [bookmark title]"` — standard ingest
- `"Silent ingest [URL or file]"` — skip discussion; update pages and log only
- `"Careful ingest [URL or file]"` — conservative mode; cap page updates at 1 to 3
- `"Ingest batch [title1], [title2], ..."` — process multiple bookmarks sequentially, then generate a daily digest
- `"Daily digest"` — summarize recent ingests into today's daily note

## Protocol

1. Read the raw source.
2. Discuss 3 to 5 key takeaways with the user unless the trigger is silent ingest.
3. Read `index.md` to identify which existing wiki pages this source touches.
4. Update existing pages first.
   - Default blast radius: 5 to 10 pages.
   - Hard cap: 15 unless the user explicitly wants a wider pass.
   - `Careful ingest` caps the pass at 1 to 3 pages.
   - Add provenance note on each touched page: `> Updated from: [[source-title]] YYYY-MM-DD`
   - Flag contradictions: `> [!] Contradiction: this conflicts with [[other-page]] — needs review`
   - Add explicit `note_type` frontmatter when creating or materially restructuring pages.
   - If the source mentions a tool, protocol, person, or concept reused by 2 or more pages but lacking a dedicated page, create one with `note_type: concept` or `note_type: entity`.
5. If the source touches 3 or more pages, create `projects/<domain>/summaries/<source-title>.md` with the source, key takeaways, and touched pages.
6. Mark the bookmark `status: processed` if it came from `raw/`.
7. Append to `log.md`:
   ```
   ## [YYYY-MM-DD] ingest | <source title>
   Pages touched: [[page1]], [[page2]], ...
   Key ideas: brief summary
   ```
8. Update `index.md` with any newly created pages.

If the index has no useful matches, fall back to a broad vault search before concluding there is no coverage.

## Daily Digest Protocol

Triggered after batch ingest or by `"Daily digest"`:

1. Read `log.md` and find ingest entries since the last digest.
2. Read the touched pages from those entries.
3. Write a `## Wiki Digest — YYYY-MM-DD` section to today's `daily_notes/YYYY-MM-DD.md`.
4. Append a digest entry to `log.md`.

## Quality Check

- At least one existing page was updated.
- `log.md` was appended.
- `index.md` reflects new pages.
- The bookmark is marked `status: processed` when applicable.
````

File: `skills/vault-query/SKILL.md`

````markdown
---
name: vault-query
description: Answer questions by synthesizing knowledge from the Obsidian vault wiki. Use when the user asks what they know about a topic, wants a synthesis, or wants connections across notes.
---

# vault-query

Answer a question by synthesizing knowledge from the vault wiki.

## Trigger

- `"What do I know about X?"`
- `"Synthesize my notes on Y"`
- `"What have I learned about Z?"`
- `"Connect X and Y"`

## Protocol

1. Read `index.md` first.
2. Read the most relevant pages and follow wikilinks as needed.
3. Synthesize the answer with inline `[[wikilink]]` citations.
   - Lead with the direct answer.
   - Use mind-map structure rather than long generic prose.
   - Surface contradictions, stale claims, or missing coverage when they matter.
4. If the synthesis is valuable and not already represented in the vault, offer to file it as a new note.
5. If the index does not surface a match, fall back to broad vault search before concluding the vault has no coverage.
6. Append to `log.md`:
   ```
   ## [YYYY-MM-DD] query | <question summary>
   Pages consulted: [[page1]], [[page2]], ...
   Key insight: one-line synthesis
   ```

## Quality Check

- Cite specific vault pages with `[[wikilinks]]`.
- Do not fabricate facts beyond what is in the vault.
- If the vault has no coverage, say so clearly and suggest an ingest.
````

File: `skills/vault-lint/SKILL.md`

````markdown
---
name: vault-lint
description: Health check the Obsidian vault wiki. Use when the user wants a vault lint, structural health check, semantic contradiction scan, or vault hygiene report.
---

# vault-lint

Health check the vault. Modes: structural, semantic, full, and reindex.

## Trigger

- `"Lint the vault"` — structural mode by default
- `"Lint the vault structural"`
- `"Lint the vault semantic"`
- `"Lint the vault full"`
- `"Reindex the vault"`

## Reindex Mode

Triggered by `"Reindex the vault"`.

Scan active content directories for files missing from `index.md`:
- `projects/**/*.md`
- `skills/**/*.md`
- top-level knowledge folders such as `golang/`, `react/`, `flutter/`, `vim/`, `nodejs/`, `php/`, `rustlang/`, `web/`, `database/`, `networking/`, `systemd/`, `hosting/`

For each missing file:
1. Read the title and first few lines.
2. Generate a one-line summary.
3. Add an `index.md` entry in the correct section.

Append to `log.md`:
```
## [YYYY-MM-DD] reindex | N new entries added
Coverage: before -> after
```

## Structural Mode

1. Read `index.md`.
2. Find broken wikilinks.
3. Find orphan pages.
4. Find stale unread bookmarks in `raw/`.
5. Find index gaps.

## Semantic Mode

1. Flag contradictions across related pages.
2. Identify missing cross-references.
3. Suggest pruning or merge candidates.
4. Flag stale claims when `last_reviewed` is old and the page contains time-sensitive facts.
5. Identify data gaps where a concept or entity should have a dedicated page.
6. Suggest 3 to 5 follow-up investigations.

## Log Entry

Append to `log.md` after lint:
```
## [YYYY-MM-DD] lint | <N issues found> (<mode>)
Broken links: N, Orphans: N, Stale: N, Index gaps: N
Contradictions: N, Missing refs: N, Pruning: N, Stale claims: N, Data gaps: N
```
````

### Step 10: Seed `index.md`

Build `index.md` after the other files are written.

#### 10.1 Crawl rules

- Include all `.md` files under the vault.
- Exclude:
  - `<vault>/AGENTS.md`
  - `<vault>/CLAUDE.md`
  - `<vault>/index.md`
  - `<vault>/log.md`
  - `<vault>/AI Note-Taking Principles.md`
  - hidden files
  - files inside hidden directories
- Convert each result to a vault-relative path using forward slashes.
- Remove the `.md` extension for the wikilink target.
- Sort entries alphabetically within each section.

#### 10.2 Section grouping

Group files into exactly these sections:

- `## Projects`
- `## Technology`
- `## Skills & Workflows`
- `## Concepts & Methodology`
- `## Ideas`
- `## Reference Notes`

Classification rules in order:

1. Paths under `projects/` -> `Projects`
2. Paths under `skills/` -> `Skills & Workflows`
3. Paths under `Ideas/` -> `Ideas`
4. Paths under obvious technology or domain folders such as `golang/`, `react/`, `flutter/`, `vim/`, `nodejs/`, `php/`, `rustlang/`, `web/`, `database/`, `networking/`, `systemd/`, `hosting/`, or any similar top-level folder -> `Technology`
5. Filenames containing words like `principles`, `method`, `methodology`, `workflow`, `playbook`, `pattern`, `concept`, `decision`, `overview`, or `guide` -> `Concepts & Methodology`
6. Everything else -> `Reference Notes`

#### 10.3 Entry format

For each indexed file, write:

`- [[relative/path/without-extension]] — <brief description or blank>`

Description rules:

- Use a short inferred description when obvious from the path or filename.
- Examples:
  - `projects/foo/overview.md` -> `project overview`
  - `projects/foo/summaries/bar.md` -> `source summary`
  - `skills/vault-ingest/SKILL.md` -> `Claude Code skill`
  - `daily_notes/2026-04-12.md` -> `daily note`
- Otherwise leave the description blank after the em dash.

#### 10.4 Exact layout

Write `<vault>/index.md` exactly as shown.

File: `index.md`

````markdown
---
aliases:
  - vault index
tags:
  - system/index
created: <TODAY>
last_reviewed: <TODAY>
note_type: overview
canonical: true
---

# Vault Index

Generated: <TODAY>
Total pages indexed: <TOTAL_PAGES>

## Projects
<PROJECT_ENTRIES_OR_- None yet>

## Technology
<TECHNOLOGY_ENTRIES_OR_- None yet>

## Skills & Workflows
<SKILL_ENTRIES_OR_- None yet>

## Concepts & Methodology
<CONCEPT_ENTRIES_OR_- None yet>

## Ideas
<IDEA_ENTRIES_OR_- None yet>

## Reference Notes
<REFERENCE_ENTRIES_OR_- None yet>
````

Substitution rules:

- Replace `<TODAY>` with today's date.
- Replace `<TOTAL_PAGES>` with the number of indexed files after exclusions.
- Replace each section placeholder with the generated bullet list.
- If a section has no entries, write exactly `- None yet`.

### Step 11: Create `log.md`

Write `<vault>/log.md` after `index.md` is final.

File: `log.md`

````markdown
# Vault Log

Append-only operation log for this vault's wiki workflows.

Rules:
- Append new entries to the end of this file.
- Do not rewrite, reorder, or summarize prior entries.
- Use dated section headings in the form `## [YYYY-MM-DD] <operation> | <summary>`.

## [<TODAY>] bootstrap | vault wiki initialized

Files created:
<CREATED_FILE_BULLETS>

Directories created:
<CREATED_DIRECTORY_BULLETS>

Skills installed:
- `skills/vault-ingest/SKILL.md`
- `skills/vault-query/SKILL.md`
- `skills/vault-lint/SKILL.md`

Notes indexed: <TOTAL_PAGES>
````

Substitution rules:

- Replace `<TODAY>` with today's date.
- Replace `<CREATED_FILE_BULLETS>` with bullets for:
  - `AGENTS.md`
  - `CLAUDE.md`
  - `AI Note-Taking Principles.md`
  - `projects/vault-llm-wiki/overview.md`
  - `projects/vault-llm-wiki/usage.md`
  - `skills/vault-ingest/SKILL.md`
  - `skills/vault-query/SKILL.md`
  - `skills/vault-lint/SKILL.md`
  - `index.md`
  - `log.md`
- Replace `<CREATED_DIRECTORY_BULLETS>` with bullets for directories actually created.
- If no new directories were created, write exactly `- None created`.
- Replace `<TOTAL_PAGES>` with the final indexed count.

### Step 12: Print confirmation

After all writes are complete, print:

```text
Vault wiki bootstrap complete.

Vault: <ABSOLUTE_VAULT_PATH>

Files created:
- <absolute path to file 1>
- <absolute path to file 2>
- <absolute path to file 3>
- <absolute path to file 4>
- <absolute path to file 5>
- <absolute path to file 6>
- <absolute path to file 7>
- <absolute path to file 8>
- <absolute path to file 9>
- <absolute path to file 10>

Directories created:
- <absolute path to directory 1>
- <absolute path to directory 2>
...

Skills installed:
- skills/vault-ingest/SKILL.md
- skills/vault-query/SKILL.md
- skills/vault-lint/SKILL.md

Total pages indexed: <TOTAL_PAGES>

Next steps:
1. Test a query: "What do I know about X?"
2. Ingest a bookmark: "Ingest <URL or file>"
3. Run lint: "Lint the vault"
4. Rebuild index coverage later with: "Reindex the vault"
```

If no new directories were created, replace the list with:

`- None created`

## Verification Checklist

- The vault path exists and is a directory.
- Existing target files were either backed up or the run was aborted.
- `AGENTS.md` exists and points agents to `CLAUDE.md`.
- `CLAUDE.md` exists and contains `# Vault Schema — Claude Operating Instructions`.
- `AI Note-Taking Principles.md` exists.
- `projects/vault-llm-wiki/overview.md` exists.
- `projects/vault-llm-wiki/usage.md` exists.
- `skills/vault-ingest/SKILL.md` exists.
- `skills/vault-query/SKILL.md` exists.
- `skills/vault-lint/SKILL.md` exists.
- `index.md` exists and its count matches the indexed files discovered by the crawl rules.
- `log.md` exists and contains the bootstrap entry for today's date.
- The final confirmation message matches what was actually written.

## Failure Handling

- If validation fails in Step 2, stop immediately.
- If the user refuses backup in Step 3, stop immediately.
- If a backup target already exists, stop immediately.
- If any file write fails, report the path that failed and stop.
- Do not claim completion unless every verification item passes.
