---
name: vault-lint
description: Health check the Obsidian vault wiki. Use when the user wants a vault lint, structural health check, semantic contradiction scan, or vault hygiene report.
---

# vault-lint

Health check the vault. Two modes: **structural** (fast, deterministic) and **semantic** (slower, LLM reasoning).

## Trigger

- `"Lint the vault"` — runs structural mode by default
- `"Lint the vault structural"` — broken links, orphans, stale bookmarks only
- `"Lint the vault semantic"` — contradictions, missing cross-references, pruning candidates
- `"Lint the vault full"` — both modes
- `"Reindex the vault"` — scan all vault directories and add missing entries to index.md

---

## Reindex Mode

Triggered by `"Reindex the vault"`.

Scan all content directories for files missing from `index.md`:
- `projects/**/*.md` — project notes
- `skills/**/*.md` — skill files
- `golang/`, `react/`, `flutter/`, `vim/`, `nodejs/`, `php/`, `rustlang/`, `web/`, `database/`, `networking/`, `systemd/` — tech knowledge bases

For each file not in `index.md`:
1. Read the file briefly (title + first 10 lines)
2. Generate a one-line summary
3. Add to the appropriate section in `index.md`:
   ```
   - [[path/to/file]] — one-line summary
   ```

Append to `log.md`:
```
## [YYYY-MM-DD] reindex | N new entries added
Coverage: before → after (N/717 files)
```

---

## Structural Mode (Deterministic)

Fast checks that have clear right/wrong answers:

1. **Read `index.md`** — baseline of all indexed pages
2. **Broken wikilinks** — index entries pointing to files that don't exist on disk
3. **Orphan pages** — indexed pages with no incoming wikilinks from other pages
4. **Stale unread bookmarks** — `raw/` files with `status: unread` and `saved` date > 30 days ago
5. **Index gaps** — files in `projects/` and `skills/` not present in `index.md`

---

## Semantic Mode (LLM Reasoning)

Slower checks requiring judgment — run separately to keep results stable:

1. **Contradictions** — read clusters of related pages; flag conflicting claims with page citations
2. **Missing cross-references** — identify clearly related pages that don't link to each other
3. **Pruning candidates** — pages that are too short, redundant, or superseded; suggest merges
4. **Suggested investigations** — 3–5 questions worth exploring given gaps found
5. **Stale claim detection** — flag pages with `last_reviewed` older than 90 days and time-sensitive claims (e.g., versions, schedules)
6. **Data gap detection** — find concepts/entities mentioned by multiple pages but lacking a dedicated page (suggest creation)

---

## Output Format

```markdown
## Vault Health Report — YYYY-MM-DD
Mode: structural | semantic | full

### Broken wikilinks (N)
- [[missing-page]] — referenced in [[source-page]]

### Orphan pages (N)
- [[page]] — no incoming links

### Stale unread bookmarks (N)
- [[raw/article]] — saved YYYY-MM-DD (N days ago)

### Index gaps (N)
- projects/foo/bar.md — not in index

--- (semantic only below) ---

### Contradictions (N)
- [[page-a]] says X; [[page-b]] says Y

### Missing cross-references (N)
- [[page-a]] and [[page-b]] are clearly related but not linked

### Pruning candidates (N)
- [[page]] — too short / redundant with [[other-page]]

### Stale claims (N)
- [[page]] — last_reviewed YYYY-MM-DD; claim "..." might be outdated

### Data gaps (N)
- [[concept-name]] — mentioned in [[page-a]], [[page-b]], but lacks a dedicated page

### Suggested investigations
1. ...
```

## Log Entry

Append to `log.md` after lint:
```
## [YYYY-MM-DD] lint | <N issues found> (<mode>)
Broken links: N, Orphans: N, Stale: N, Index gaps: N
Contradictions: N, Missing refs: N, Pruning: N, Stale claims: N, Data gaps: N
```

## Related

- [[CLAUDE.md]] — vault schema
- [[index.md]] — primary reference for all pages
- [[log.md]] — append after lint
