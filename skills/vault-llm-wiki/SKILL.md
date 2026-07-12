---
name: vault-llm-wiki
description: Core protocol for the compounding Obsidian vault wiki — ingest, query, and lint an Obsidian vault as a durable second brain. Shared home for the vault-ingest, vault-query, and vault-lint protocols and the in-vault control-file templates.
---

# vault-llm-wiki

The single source for how agents operate the compounding wiki inside an Obsidian
vault: an append-only, index-first knowledge layer that gets richer with every
source instead of accumulating isolated notes.

This core states only the **vault-specific** protocol. The shared wiki invariants
— index-first lookup, `[[wikilink]]` citation, thicken-before-create,
`Updated from <title> YYYY-MM-DD` provenance, contradiction flagging, an
append-only `log.md`, and the blast-radius hard cap of 15 touched pages — are
defined once in `../project-llm-wiki/references/wiki-conventions.md` and apply to
every mode below.

## Trigger

Use this skill when the user wants to ingest into, query, or lint an Obsidian
vault wiki. Recognized trigger phrases:

- `"Ingest [source]"`, `"Process [bookmark]"`, `"Silent ingest [source]"`,
  `"Careful ingest [source]"`, `"Ingest batch [A], [B], [C]"`, `"Daily digest"`
- `"What do I know about X?"`, `"Synthesize my notes on Y"`,
  `"What have I learned about Z?"`, `"Connect X and Y"`
- `"Lint the vault"` (and `structural` / `semantic` / `full` variants),
  `"Reindex the vault"`

## Protocol

The **vault is the source of truth** — the maintained AI second brain and the
primary reference for knowledge lookups, prior ingest status, project context,
and long-term memory. Prefer the vault over workspace-local memory or chat
summaries when they conflict, unless the user says otherwise.

Read the vault's `index.md` first (per the shared invariants), then open only the
task-relevant pages. `AGENTS.md` points agents to `CLAUDE.md`; `CLAUDE.md` holds
the vault schema, page types, and frontmatter conventions.

### Maintenance trio vs. thinking aids

Two families of skills read the same vault, but only one family maintains it:

- **Maintenance trio** — `vault-ingest`, `vault-query`, and `vault-lint` are the
  only skills that write durable wiki content. They own the ingest/query/lint
  protocols in the Modes below and are the surfaces that touch pages, `index.md`,
  and `log.md`.
- **Thinking aids** — `vault-challenge`, `vault-connect`, `vault-ghost`,
  `vault-ideas`, `vault-today`, and `vault-trace` read and reason over the vault
  but do not maintain it. They consume the wiki the trio curates; they never
  substitute for ingest/query/lint and do not silently rewrite pages.

## Modes

### Ingest (`vault-ingest`)

Compounding update: update existing pages first, do not default to isolated new
notes.

Trigger variants: standard ingest (with discussion), `Silent ingest` (skip
discussion), `Careful ingest` (conservative mode), `Ingest batch` (multiple
sources, then a Daily Digest), and `Daily digest`.

1. Read the raw source (fetch URL or read file).
2. Discuss 3–5 key takeaways with the user — skip this step for `Silent ingest`.
3. Read `index.md` to identify which existing wiki pages the source touches.
4. Update existing pages first.
   - **Default blast radius: 5–10 pages.** Touch more only when clearly
     warranted, up to the shared hard cap of 15.
   - **`Careful ingest` caps the pass at 1–3 pages** for reviewability.
   - Provenance on each touched page: `> Updated from: [[source-title]] YYYY-MM-DD`.
   - Flag contradictions: `> [!] Contradiction: this conflicts with [[other-page]] — needs review`.
   - Add explicit `note_type` frontmatter when creating or materially
     restructuring pages.
   - If a tool, protocol, person, or concept is reused by 2+ pages but lacks a
     dedicated page, create one (`note_type: concept` or `note_type: entity`).
5. If the source touches 3+ pages, create a summary at
   `projects/<domain>/summaries/<source-title>.md` with the source link, key
   takeaways, and touched pages.
6. Mark the bookmark `status: processed` if it came from `raw/`.
7. Append an ingest entry to `log.md` (source title, pages touched, key ideas).
8. Update `index.md` with any newly created pages.

If the index surfaces no relevant pages, fall back to a broad vault search before
concluding there is no coverage.

**Daily Digest** (after batch ingest or `"Daily digest"`): read `log.md` for
ingest entries since the last digest, read the touched pages, write a
`## Wiki Digest — YYYY-MM-DD` section to today's `daily_notes/YYYY-MM-DD.md`, and
append a digest entry to `log.md`.

### Query (`vault-query`)

Answer a question by synthesizing knowledge from the vault.

1. Read `index.md` first, then read the relevant pages, following wikilinks as
   needed.
2. Synthesize with inline `[[wikilink]]` citations. Lead with the direct answer;
   use mind-map structure (headers, bullets), not long prose; surface
   contradictions or gaps when they matter.
3. If a valuable synthesis is not yet represented in the vault, offer to file it
   as a new note.
4. If the index has no match, fall back to a broad vault search before concluding
   there is no coverage.
5. Append a query entry to `log.md` (question summary, pages consulted, key
   insight). Do not fabricate facts beyond what the vault contains; if the vault
   has no coverage, say so clearly and suggest an ingest.

### Lint (`vault-lint`)

Health check the vault. Modes: `structural` (fast, deterministic), `semantic`
(LLM reasoning), `full` (both), and `reindex`.

- **Structural** — broken wikilinks, orphan pages, stale unread bookmarks in
  `raw/` (`status: unread` older than 30 days), and index gaps
  (`projects/` and `skills/` files missing from `index.md`).
- **Semantic** — contradictions across related pages, missing cross-references,
  pruning/merge candidates, stale claims (`last_reviewed` older than 90 days and
  time-sensitive facts present), data gaps (concepts/entities reused across pages but lacking a
  dedicated page), and 3–5 suggested investigations.
- **Reindex** — scan active content directories (`projects/**`, `skills/**`, and
  top-level knowledge folders), add missing files to `index.md` with a one-line
  summary, and append a reindex entry to `log.md`.

Append a lint entry to `log.md` after every run (issue counts by category and the
mode used).

## In-vault control files

The vault's control-file templates are maintained here, in
`assets/templates/vault/`, as the single source:

- `AGENTS.md` — Codex entrypoint that points agents to `CLAUDE.md`.
- `CLAUDE.md` — vault schema, page types, frontmatter, and operating contract.
- `AI Note-Taking Principles.md` — mind-map note style guide.
- `index.md` — seeded catalog of wiki pages; read first on every query.
- `log.md` — append-only operation log.

## Safety Boundaries

- Never silently overwrite an existing control file when bootstrapping a vault;
  back up or abort instead.
- Keep only curated, durable knowledge in the vault. Never store full
  transcripts, full logs, dumps, secrets, private data, or active task state.
- Respect the shared blast-radius cap defined in
  `../project-llm-wiki/references/wiki-conventions.md`: stop and ask for a human
  decision before exceeding it.

## Quality Check

- The core cites `../project-llm-wiki/references/wiki-conventions.md` for the
  shared invariants rather than restating them, and ships no copy of that file.
- The vault-specific values live here: vault = source of truth, ingest 5–10
  default / careful 1–3, and the maintenance-trio-vs-thinking-aids split.
- The in-vault control-file templates stay a single maintained source under
  `assets/templates/vault/`.
- Run `python3 -m unittest discover -s skills/project-llm-wiki/tests` after
  changes to this package.

## Related

- `../project-llm-wiki/references/wiki-conventions.md` — shared wiki invariants
- `assets/templates/vault/` — in-vault control-file templates
