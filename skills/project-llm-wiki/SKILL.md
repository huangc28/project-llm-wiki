---
name: project-llm-wiki
description: Create and maintain a repo-local .llm-wiki/ knowledge layer for durable project context.
---

# project-llm-wiki

## Trigger

Use this skill when the user asks to create, initialize, query, lint, ingest, or maintain a repo-local Project LLM Wiki.

Recognized trigger phrases:

- `project-wiki-init`
- `project-wiki-lint`
- `project-wiki-query`
- `project-wiki-ingest`

## Protocol

Read the target repository's git root before writing .llm-wiki/.

Keep durable, validated project knowledge in `.llm-wiki/`. Do not store active task state in .llm-wiki/.

Trust current repo code over .llm-wiki/ when they disagree.

Phase 1 documents the package surface; later phases implement full mode behavior.

## Modes

`project-wiki-init` creates the initial `.llm-wiki/` skeleton in the target repository's actual git root. Full behavior is implemented in Phase 2.

`project-wiki-lint` checks wiki structure, safety, freshness, and repo/wiki drift. Full behavior is implemented in Phase 3.

`project-wiki-query` answers from `.llm-wiki/index.md` and related pages with repo-local wikilink citations.

Query protocol:

1. Resolve the target repository's Git root.
2. Read .llm-wiki/index.md first.
3. Inspect the relevant linked wiki pages before answering.
4. Direct claims require `[[wikilink]]` citations to repo-local wiki pages.
5. Put synthesis or cross-page reasoning under an `Inference` section.
6. If `.llm-wiki/` does not currently cover the topic, say that clearly, list pages consulted, and suggest the source type to ingest next.
7. Append a concise query entry to `.llm-wiki/log.md` with date, query summary, pages consulted, and key insight or not-covered result.

Do not store full transcripts, complete question/answer chat history, or unvalidated task notes in `.llm-wiki/log.md`.

`project-wiki-ingest` updates durable wiki pages from curated, de-secreted project sources. Full behavior is implemented in Phase 4.

## Safety Boundaries

Do not initialize `.llm-wiki/` in a multi-repo parent directory unless the parent is the intended git repository.

Do not store secrets, credentials, private customer data, auth tokens, full logs, database exports, generated dumps, or unvalidated task notes in `.llm-wiki/`.

Do not install or modify global skill directories during Phase 1.

## Quality Check

Run `python3 -m unittest discover -s skills/project-llm-wiki/tests` after package changes.

## Related

- `references/command-surface.md`
- `references/package-contract.md`
