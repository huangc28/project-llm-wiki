# Wiki Conventions

Shared invariants for every `.llm-wiki/`-style knowledge layer — the repo-local
Project LLM Wiki and the Obsidian vault wiki alike. Each core cites this file instead
of restating these rules. Profile-specific values (page budgets, read caps) live in the
individual skill prose, never here.

## Lookup

- **Index-first lookup.** Read the wiki's `index.md` first, then open only the
  task-relevant linked pages. Never default to a full scan of every page.

## Citation

- **`[[wikilink]]` citation.** Every direct claim cites the wiki page it came from with
  an Obsidian `[[wikilink]]`. Synthesis that spans pages goes under a labeled
  `Inference` section, kept separate from cited claims.

## Updating pages

- **Thicken before creating.** Update an existing page before creating a new one. Create
  a new page only with an explicit reason that no existing page covers the concept or
  that it deserves a durable cross-page home.
- **Provenance.** Every touched page records concise provenance in the form
  `Updated from <title> YYYY-MM-DD`.
- **Flag contradictions.** When a new source contradicts an existing page, flag the
  contradiction explicitly rather than silently overwriting. Preserve both the prior
  claim and the new one until a human resolves it.

## Log discipline

- **Append-only log.** `log.md` is append-only: never rewrite, reorder, or summarize
  existing entries. Add new entries under dated headings. Store only pages touched and
  key ideas — never full transcripts, chat history, dumps, or unvalidated task notes.

## Blast radius

- **Blast-radius hard cap = 15.** A single ingest or update touches at most 15 pages.
  Stop and ask for a human decision before exceeding the cap.
