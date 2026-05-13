# Testing

## Test Commands

Run package tests with:

`python3 -m unittest discover -s skills/project-llm-wiki/tests`

Run the targeted Phase 3 lint suite with:

`python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_lint.py`

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

## No Dependency Rule

The helper script should stay on the Python standard library. The import
whitelist test must be updated only when `project_wiki.py` actually imports a new
standard-library module.

Tests should use Python standard-library modules only.
