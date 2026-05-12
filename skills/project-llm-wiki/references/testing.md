# Testing

## Test Command

Run package tests with:

`python3 -m unittest discover -s skills/project-llm-wiki/tests`

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

## No Dependency Rule

The helper script should stay on the Python standard library. The import
whitelist test must be updated only when `project_wiki.py` actually imports a new
standard-library module.

Tests should use Python standard-library modules only.
