---
name: vault-ingest
description: Ingest a raw source into the Obsidian vault wiki. Use when the user wants to ingest or process a bookmark, URL, file, or source into existing vault notes with compounding updates.
---

# vault-ingest

Ingest a raw source into the vault wiki. Updates existing pages (compounding), does not just create isolated new notes.

## Trigger

- `"Ingest [URL or file]"` or `"Process [bookmark title]"` — standard ingest (with discussion)
- `"Silent ingest [URL or file]"` — skip discussion; just update pages and log (for low-priority sources)
- `"Careful ingest [URL or file]"` — conservative mode; caps page updates at 1–3 (for reviewability)
- `"Ingest batch [title1], [title2], ..."` — process multiple bookmarks sequentially, then generate a Daily Digest
- `"Daily digest"` — summarize all ingests since last digest into today's `daily_notes/YYYY-MM-DD.md`

## Protocol

1. **Read** the raw source (fetch URL or read file)
2. **Discuss** 3–5 key takeaways with the user — confirm what matters before writing
   *(Skip this step if triggered as "Silent ingest")*
3. **Read `index.md`** to identify which existing wiki pages this source touches
4. **Update existing pages first** — default to **5–10 pages**; touch more only when clearly warranted (max 15)
   - Use `"Careful ingest [source]"` trigger to cap at 1–3 pages when conservative mode is needed
   - Add provenance note on each touched page: `> Updated from: [[source-title]] YYYY-MM-DD`
   - Flag contradictions: `> [!] Contradiction: this conflicts with [[other-page]] — needs review`
   - Only create a new page when no existing page covers the concept. Explicitly include `note_type` in the frontmatter for new or updated pages.
   - **Entity/Concept Pages**: If the source mentions a tool, protocol, person, or concept referenced by 2+ pages but lacking a dedicated page, create one (e.g., `note_type: concept` or `note_type: entity`).
4.5. **Source Summary Page**: If the source touches 3+ pages, create a wiki-layer summary at `projects/<domain>/summaries/<source-title>.md` (inferring the domain). Include the source link, key takeaways, and a list of all touched pages.
5. **Mark the bookmark** `status: processed` if it came from `raw/`
6. **Append to `log.md`**:
   ```
   ## [YYYY-MM-DD] ingest | <source title>
   Pages touched: [[page1]], [[page2]], ...
   Key ideas: brief summary
   ```
7. **Update `index.md`** — add entries for any newly created pages

## Daily Digest Protocol

Triggered after batch ingest or by `"Daily digest"`:

1. Read `log.md` — find all ingest entries since last digest
2. Read the touched pages from those entries
3. Write a "What's New in the Wiki" section to today's `daily_notes/YYYY-MM-DD.md`:
   ```markdown
   ## Wiki Digest — YYYY-MM-DD
   - [[source-A]] → updated [[page-1]], [[page-2]] — key idea
   - [[source-B]] → created [[new-page]] — key idea
   ```
4. Append to `log.md`: `## [YYYY-MM-DD] digest | N sources processed`

## Quality Check

Before finishing, verify:
- At least one existing page was updated (not just new pages created)
- `log.md` has been appended
- `index.md` reflects any new pages
- The source bookmark (if applicable) is marked `status: processed`

## Related

- [[CLAUDE.md]] — vault schema and page type conventions
- [[AI Note-Taking Principles]] — style guide (mind-map, wikilinks, concise)
- [[index.md]] — read first to find pages to update
- [[log.md]] — append after every ingest
