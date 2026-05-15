# Command Surface

## Current Contract

The package documents mode names and boundaries for the reusable Project LLM Wiki skill. Implemented modes are safe to run through the helper script; deferred modes remain documented so future phases do not change command names accidentally.

The reusable package exposes one `project-llm-wiki` skill plus thin alias skills for the implemented mode triggers. The alias skills exist so Codex can show `$project-wiki-*` entries in skill autocomplete while keeping the detailed protocol in `project-llm-wiki`.

## Modes

### project-wiki install

Implemented installer mode for linking the reusable Project LLM Wiki skill package into a Codex skills directory.

Install into `${CODEX_HOME:-~/.codex}/skills`:

`project-wiki install`

Preview symlink changes without writing:

`project-wiki install --dry-run`

Install into an explicit Codex skills directory:

`project-wiki install --target PATH`

Replace stale symlinks that point somewhere else:

`project-wiki install --force`

Remove only Project LLM Wiki symlinks owned by this package:

`project-wiki install --uninstall`

Install creates symlinks for `project-llm-wiki`, `project-wiki-init`, `project-wiki-lint`, `project-wiki-query`, and `project-wiki-ingest`. Correct existing symlinks are no-ops. Existing real files or directories are conflicts. Existing symlinks that point somewhere else are conflicts unless `--force` is present. Uninstall preserves foreign symlinks and real directories.

Install does not initialize a target repository, create `.llm-wiki/`, or patch root `AGENTS.md`. Repository mutation stays behind `project-wiki init` inside the target repo's actual Git root.

### project-wiki-init

Implemented mode for detecting the current repository's actual Git root, creating an idempotent `.llm-wiki/` skeleton, and patching root `AGENTS.md` with a short Project LLM Wiki managed section when safe.

Initialize the current Git root:

`project-wiki init`

Preview all init effects without writing:

`project-wiki init --dry-run`

Initialize `.llm-wiki/` while intentionally skipping root `AGENTS.md` patching:

`project-wiki init --no-patch-agents`

By default, init patches root AGENTS.md with a short Project LLM Wiki managed section when safe.

--dry-run reports both .llm-wiki skeleton effects and root AGENTS.md effects, including the exact managed section.

--no-patch-agents skips root AGENTS.md patching.

Invalid UTF-8, unmatched Project LLM Wiki markers, or multiple Project LLM Wiki marker pairs are conflicts.

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

Implemented mode for updating existing wiki pages from curated, de-secreted project sources before creating new pages.

Ingest curated text into an existing page:

`project-wiki ingest --text TEXT --title TITLE --target-page PAGE --key-idea TEXT`

Ingest curated file content:

`project-wiki ingest --file PATH --title TITLE --target-page PAGE --key-idea TEXT`

Use a URL as provenance with curated text:

`project-wiki ingest --url URL --text CURATED_TEXT --title TITLE --target-page PAGE --key-idea TEXT`

Create a new durable page only with an explicit reason:

`project-wiki ingest --text TEXT --title TITLE --new-page PAGE --new-page-reason TEXT --key-idea TEXT`

Preserve a short curated raw source note when policy allows:

`project-wiki ingest --text TEXT --title TITLE --target-page PAGE --key-idea TEXT --preserve-raw`

Video sources require transcript, summary, or curated notes before core ingest. `$watch-video` can be a user-local preprocessor, but it is not a dependency of Project LLM Wiki core ingest.

`--preserve-raw` is optional and policy-gated. The helper rejects secrets, full transcripts, full logs, dumps, private data, active task state, execution checkpoints, oversized source material, and more than 15 touched pages.

### project-wiki-promote

Future mode for promoting validated GSD, PR, debug, or incident learnings into `.llm-wiki/` without copying volatile task state.

## Alias Skills

Implemented thin aliases:

- `$project-wiki-init`
- `$project-wiki-lint`
- `$project-wiki-query`
- `$project-wiki-ingest`

Each alias reads the main `project-llm-wiki` skill and follows its matching mode. Keep aliases thin; do not duplicate the full protocol in each wrapper.

Potential future alias:

- `$project-wiki-promote`

## Deferred Behavior

The remaining planned command surface is:

- Promotion of validated learnings into .llm-wiki/
