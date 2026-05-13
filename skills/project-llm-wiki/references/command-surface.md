# Command Surface

## Current Contract

The package documents mode names and boundaries for the reusable Project LLM Wiki skill. Implemented modes are safe to run through the helper script; deferred modes remain documented so future phases do not change command names accidentally.

The reusable package exposes one `project-llm-wiki` skill with documented mode triggers. Later phases may add thin aliases if usage proves that separate skill entrypoints are better.

## Modes

### project-wiki-init

Implemented mode for detecting the current repository's actual Git root and creating an idempotent `.llm-wiki/` skeleton.

### project-wiki-lint

Implemented read-only mode for checking broken wikilinks, missing index entries, secret-looking content, oversized raw files, stale pages, and conservative repo path drift.

Run the human-readable report:

`project-wiki lint`

Run the parseable report for CI or agent tooling:

`project-wiki lint --json`

Broken Obsidian wikilinks are `error` findings and make lint exit `1`. Missing index entries, secret-looking content, oversized raw files, stale pages, and repo path drift are `warning` findings; warning-only runs exit `0`.

Every finding contains the fixed fields `severity`, `code`, `path`, `message`, and `remediation`. Text output prints those labels for each finding. JSON output renders:

```json
{
  "findings": [
    {
      "code": "broken_wikilink",
      "message": "Human-readable problem statement.",
      "path": ".llm-wiki/features/ideas.md",
      "remediation": "Actionable repair guidance.",
      "severity": "error"
    }
  ]
}
```

Clean runs print `No issues found in .llm-wiki/` for text output and `{"findings": []}` for JSON output.

### project-wiki-query

Implemented support mode for reading `.llm-wiki/index.md` first, preparing candidate repo-local wiki pages, and appending bounded query history to `.llm-wiki/log.md`.

Prepare a human-readable support packet:

`project-wiki query QUESTION`

Prepare a parseable support packet:

`project-wiki query QUESTION --json`

Append a query log entry after the agent answers:

`project-wiki query QUESTION --consulted PAGE --key-insight TEXT`

Append a conservative not-covered log entry:

`project-wiki query QUESTION --not-covered --suggest-source TEXT`

The helper does not generate final semantic answers. Agents still read the returned candidate pages, answer with direct claims cited by `[[wikilink]]`, put synthesis under a labeled `Inference` section, and use a not-covered response when the current wiki lacks evidence.

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

- Query and ingest loop: Phase 4
- Promotion of validated learnings into `.llm-wiki/`
- AGENTS integration and real repo validation: Phase 5
