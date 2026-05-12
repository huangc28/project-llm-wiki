# Command Surface

## Phase 1 Contract

Phase 1 documents mode names and boundaries. It does not implement full `.llm-wiki/` init, lint, query, ingest, promotion, or AGENTS patch behavior.

The reusable package exposes one `project-llm-wiki` skill with documented mode triggers. Later phases may add thin aliases if usage proves that separate skill entrypoints are better.

## Modes

### project-wiki-init

Planned mode for detecting the target repository's actual git root and creating an idempotent `.llm-wiki/` skeleton.

### project-wiki-lint

Planned mode for checking broken wikilinks, missing index entries, secret-looking content, oversized raw files, stale pages, and likely repo/wiki contradictions.

### project-wiki-query

Planned mode for reading `.llm-wiki/index.md` first, answering with repo-local `[[wikilink]]` citations, and appending query history to `.llm-wiki/log.md`.

### project-wiki-ingest

Planned mode for updating existing wiki pages from curated, de-secreted project sources before creating new pages.

### project-wiki-promote

Future mode for promoting validated GSD, PR, debug, or incident learnings into `.llm-wiki/` without copying volatile task state.

## Planned Aliases

The primary package remains `project-llm-wiki` during Phase 1.

Potential future aliases:

- `project-wiki-init`
- `project-wiki-lint`
- `project-wiki-query`
- `project-wiki-ingest`
- `project-wiki-promote`

## Deferred Behavior

Full command behavior is deferred to later phases:

- Init and wiki templates: Phase 2
- Lint and safety checks: Phase 3
- Query and ingest loop: Phase 4
- AGENTS integration and real repo validation: Phase 5
