# Testing

## Test Commands

Run package tests with:

`python3 -m unittest discover -s skills/project-llm-wiki/tests`

Run the targeted Phase 3 lint suite with:

`python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_lint.py`

Run the targeted Phase 4 query suite with:

`python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_query.py`

Run the targeted Phase 4 ingest suite with:

`python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_ingest.py`

## Phase 2 Validation Contract

Phase 2 tests verify the init behavior before production implementation turns the
suite green. The Wave 0 validation fixtures use clean temporary Git repositories
so init behavior is tested through the same subprocess boundary users will run.

The validation suite covers:

- Git-root initialization from clean temporary Git repositories and nested
  subdirectories.
- `git status --short` visibility for generated `.llm-wiki/` files.
- `init --dry-run` reporting without filesystem side effects.
- idempotency for reruns that must preserve existing wiki notes.
- Conflict preflight before partial writes.
- README/AGENTS-only seed-source behavior.
- raw policy content for unsafe raw sources and curated raw guidance.

During Plan 02-03, the RED gate is:

`python3 -c 'import subprocess, sys; result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "skills/project-llm-wiki/tests"]); sys.exit(0 if result.returncode != 0 else 1)'`

After Plans 02-01 and 02-02 implement init behavior, the expected green command
is:

`python3 -m unittest discover -s skills/project-llm-wiki/tests`

## Phase 3 Validation Contract

Phase 3 tests verify lint behavior through clean temporary Git repositories that
run `project-wiki init`, mutate `.llm-wiki/`, and then run `project-wiki lint`
through the same subprocess boundary users will run.

The validation suite covers:

- broken wikilinks as error findings and exit code `1`.
- missing index entries as warning findings and warning-only exit behavior.
- secret-looking content in Markdown and non-Markdown raw files.
- oversized raw files under `.llm-wiki/raw/`.
- stale pages using top-of-file `updated:` frontmatter older than 90 days.
- repo path drift from inline code spans and fenced code blocks only.
- JSON output from `project-wiki lint --json`.
- fixed finding fields: `severity`, `code`, `path`, `message`, and
  `remediation`.
- read-only assertions that compare wiki file bytes before and after warning and
  error lint runs.

## Phase 4 Validation Contract

Phase 4 tests verify the query and ingest loop through clean temporary Git
repositories that run `project-wiki init`, seed wiki pages or source material,
and then run `project-wiki query` or `project-wiki ingest` through the same
subprocess boundary users will run.

The query validation suite covers:

- QUERY-01: `project-wiki query` reads `.llm-wiki/index.md` first and returns
  candidate `[[wikilink]]` pages from the index.
- QUERY-02: query support output states that direct claims require
  `[[wikilink]]` citations and does not emit final semantic answers.
- QUERY-03: not-covered query flow records consulted pages and suggests a source
  type to ingest next.
- QUERY-04: query runs append concise `.llm-wiki/log.md` entries with pages
  consulted and key insight.
- TEST-03: seeded query fixtures prove cited-answer support, JSON packet output,
  and log append behavior without making Python synthesize final answers.

The ingest validation suite covers:

- INGEST-01: text, file, and URL-provenance curated sources are accepted, while
  unsafe raw material is rejected.
- INGEST-02: ingest prefers existing page updates before creating new pages.
- INGEST-03: summary pages require explicit cross-cutting intent via
  `--summary-page`.
- INGEST-04: touched pages receive provenance, new pages update `index.md`, and
  ingest appends `log.md`.
- INGEST-05: full logs, full transcripts, active task state, execution
  checkpoints, secrets, private data, oversized sources, and parent-directory
  page targets are rejected.

video sources require transcript, summary, or curated notes before core ingest.
`$watch-video` can be a local preprocessing helper, but it is not required by
Project LLM Wiki.

## No Dependency Rule

The helper script should stay on the Python standard library. The import
whitelist test must be updated only when `project_wiki.py` actually imports a new
standard-library module.

Tests should use Python standard-library modules only.
