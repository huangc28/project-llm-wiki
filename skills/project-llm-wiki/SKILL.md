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

Use `.llm-wiki/index.md` as the entry point for non-trivial wiki lookups, then read only task-relevant linked pages.

## Modes

`project-wiki-init` creates the initial `.llm-wiki/` skeleton in the target repository's actual git root and patches root `AGENTS.md` by default when safe.

Use `project-wiki init --dry-run` to preview both `.llm-wiki/` and root `AGENTS.md` effects without writing.

Use `project-wiki init --no-patch-agents` to skip root `AGENTS.md` patching intentionally.

Root `AGENTS.md` guidance tells agents to read `.llm-wiki/index.md` before non-trivial architecture, debugging, product, onboarding, or cross-file implementation work.

Root `AGENTS.md` guidance states simple typo fixes and narrow single-file edits do not require wiki lookup.

Root `AGENTS.md` guidance uses index-first, relevant-pages-only lookup rather than default full scans of `.llm-wiki/`.

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

`project-wiki-ingest` updates durable wiki pages from curated, de-secreted project sources.

Ingest protocol:

1. Accept curated text, curated file content, or URL provenance paired with curated text.
2. Video sources require transcript, summary, or curated notes before core ingest.
3. `$watch-video` can be a user-local preprocessor, but Project LLM Wiki core ingest must not depend on it.
4. Ingest updates existing pages before creating new pages.
5. Create a new page only with an explicit reason that no existing page covers the concept or the concept deserves a durable cross-page home.
6. Every touched page gets concise provenance such as `Updated from <title> YYYY-MM-DD`.
7. `index.md` is updated only for newly created pages.
8. `log.md` records pages touched and key ideas.

Raw curated storage is optional and policy-gated with `--preserve-raw`. Never store full transcripts, full logs, dumps, secrets, private data, active task state, execution checkpoints, or large unreviewed raw material. The page hard cap is 15 touched pages.

## Safety Boundaries

Do not initialize `.llm-wiki/` in a multi-repo parent directory unless the parent is the intended git repository.

Do not store secrets, credentials, private customer data, auth tokens, full logs, database exports, generated dumps, or unvalidated task notes in `.llm-wiki/`.

For ingest, Never store full transcripts, full logs, dumps, secrets, private data, active task state, or execution checkpoints. The blast-radius hard cap is 15 touched pages.

Do not install or modify global skill directories during Phase 1.

## Quality Check

Run `python3 -m unittest discover -s skills/project-llm-wiki/tests` after package changes.

## Related

- `references/command-surface.md`
- `references/package-contract.md`
