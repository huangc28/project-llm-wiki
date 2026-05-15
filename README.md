# Project LLM Wiki

Agents and contributors lose project context between sessions. Repos accumulate decisions, runbooks, and architectural notes that live only in chat history, PR comments, or someone's head — so the next agent re-derives them from scratch and the next contributor asks the same questions.

Project LLM Wiki adds a small, git-tracked `.llm-wiki/` knowledge layer to an existing repository, so durable project context lives next to the code that depends on it.

Use it for: architecture notes, decisions, domain concepts, runbooks, feature summaries, validated implementation learnings.
Keep elsewhere: active task state (`.planning/`, Linear, debug notes, workflow files, PR threads).

## Status

This is the reusable Phase 1 skill package. It targets Codex via `AGENTS.md` patching. There is no installer yet — the Install section below uses manual symlinks, and the helper script is location-agnostic so you can also run it from a clone. Claude Code and other runtimes are out of scope for this phase.

## Install

Two paths, both supported:

```bash
# Option A — install as Codex skills (recommended for daily use).
# Run from the project-llm-wiki repo root:
ln -s "$(pwd)/skills/project-llm-wiki"    ~/.codex/skills/
ln -s "$(pwd)/skills/project-wiki-init"   ~/.codex/skills/
ln -s "$(pwd)/skills/project-wiki-lint"   ~/.codex/skills/
ln -s "$(pwd)/skills/project-wiki-query"  ~/.codex/skills/
ln -s "$(pwd)/skills/project-wiki-ingest" ~/.codex/skills/

# Option B — run the helper script directly from the clone (no install required):
python3 ./skills/project-llm-wiki/scripts/project_wiki.py --help
```

The helper script discovers its template assets relative to its own location, so both paths work without configuration.

## Quick Start

`$skill-name` invokes a Codex skill in the current session. After installing the aliases (Option A above), open a new Codex session in any target repo and use:

```text
$project-wiki-init
$project-wiki-lint
$project-wiki-query: What does this repo wiki know about the auth flow?
$project-wiki-ingest: Add this curated note to the wiki: ...
```

The alias skills are thin wrappers around the main skill at:

```text
skills/project-llm-wiki/SKILL.md
```

## What `init` Produces

Running `$project-wiki-init` (or the CLI equivalent) in a target repo creates:

```text
.llm-wiki/
├── README.md           # human-facing overview
├── AGENTS.md           # wiki-level guidance for agents
├── index.md            # entry point — read this first
├── log.md              # validated-learning log
├── architecture/       # .gitkeep, populated on demand
├── decisions/          # .gitkeep, populated on demand
├── domain/             # .gitkeep, populated on demand
├── operations/         # .gitkeep, populated on demand
├── features/ideas.md
├── summaries/repo-overview.md
└── raw/
    ├── README.md
    └── curated/README.md
```

`.llm-wiki/index.md` is the canonical entry point, with headings for Architecture, Domain, Decisions, Operations, Features, Summaries, and Raw Sources.

Init also patches the target repo's root `AGENTS.md` with a managed section between these markers:

```text
<!-- PROJECT-LLM-WIKI:START -->
## Project LLM Wiki
...
<!-- PROJECT-LLM-WIKI:END -->
```

Content outside those markers is preserved byte-for-byte. Re-running init updates the section in place without duplicating it.

## Updating Existing Repos

If a project already uses an older Project LLM Wiki setup, re-run the same init flow. First update or reinstall this skill package (re-run the symlink commands or `git pull` in the clone), then run `$project-wiki-init` in the target repo's git root.

The alias initializes or updates the repo by default. Re-running is idempotent: existing `.llm-wiki/` notes are preserved, missing skeleton files are added, and root `AGENTS.md` is patched in place when there are no conflicts.

If you want to inspect the update before writing, pass `--dry-run`:

```bash
python3 ./skills/project-llm-wiki/scripts/project_wiki.py init --dry-run
```

The dry-run prints: paths that would be created, paths that would be skipped (existing), the action taken on root `AGENTS.md`, the exact managed section content, and any conflicts. Conflicts must be empty before applying. See `skills/project-llm-wiki/references/command-surface.md` for the full output structure.

Use `--no-patch-agents` to update `.llm-wiki/` without touching root `AGENTS.md`.

## CLI Fallback

The helper script works from any path. Set `SKILL` once:

```bash
SKILL=~/.codex/skills/project-llm-wiki   # if you symlinked
# or
SKILL=./skills/project-llm-wiki          # if running from the clone
```

Then:

```bash
# Preview initialization
python3 $SKILL/scripts/project_wiki.py init --dry-run

# Create .llm-wiki/ in the current repo's git root
python3 $SKILL/scripts/project_wiki.py init

# Lint the wiki (add --json for machine-readable output)
python3 $SKILL/scripts/project_wiki.py lint

# Prepare an index-first query support packet
python3 $SKILL/scripts/project_wiki.py query "What does the wiki know about onboarding?"

# Ingest a curated note into an existing page
python3 $SKILL/scripts/project_wiki.py ingest \
  --text "Auth uses JWT access tokens and refresh rotation." \
  --title "Auth implementation note" \
  --target-page architecture/auth \
  --key-idea "Auth uses JWT access tokens and refresh rotation."
```

Key flags worth knowing:

- `init`: `--dry-run`, `--no-patch-agents`
- `lint`: `--json`
- `query`: `--consulted PAGE`, `--key-insight TEXT`, `--not-covered`, `--json`
- `ingest`: `--text` / `--file` / `--url`, `--title`, `--target-page`, `--new-page` (with `--new-page-title`, `--new-page-reason`), `--key-idea`, `--preserve-raw`, `--summary-page`, `--json`

Full command surface and flag semantics: `skills/project-llm-wiki/references/command-surface.md`.

## Modes

| Mode | Purpose |
| --- | --- |
| `project-wiki-init` | Create the `.llm-wiki/` skeleton in the current Git repo. |
| `project-wiki-lint` | Check wiki structure, broken links, stale notes, unsafe raw material, and repo/wiki drift. |
| `project-wiki-query` | Read `.llm-wiki/index.md` first and answer with repo-local `[[wikilink]]` citations. |
| `project-wiki-ingest` | Add curated source notes to existing pages first; create new pages only with a reason. |

## Why not `.planning/` or NotebookLM?

`.planning/` tracks active workflow state — volatile, agent-mutable, not durable. NotebookLM can answer questions but its content isn't reviewable in PR diffs and doesn't travel with the repo. `.llm-wiki/` is git-tracked, curated, and lives next to the code it describes — so changes are diffable, reviewable, and recoverable from `git log`.

## Safety Rules

- Run init from the actual project repo, not a multi-repo parent folder.
- Trust current code over `.llm-wiki/` if they disagree.
- Store only curated, validated, non-secret knowledge in `.llm-wiki/`.
- Do not store full transcripts, full logs, dumps, secrets, private data, active task state, or execution checkpoints.
- Prefer updating existing pages before creating new pages.
- Use `--preserve-raw` only for short, policy-safe curated raw notes.

## Package Layout

```text
skills/project-llm-wiki/          Main skill, helper script, references, tests
skills/project-wiki-init/         Thin Codex alias skill
skills/project-wiki-lint/         Thin Codex alias skill
skills/project-wiki-query/        Thin Codex alias skill
skills/project-wiki-ingest/       Thin Codex alias skill
```

Useful references:

- `skills/project-llm-wiki/references/command-surface.md`
- `skills/project-llm-wiki/references/testing.md`
- `skills/project-llm-wiki/references/package-contract.md`

## Development

The helper is Python standard library only. Run the package test suite after changes:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests
```

The current suite covers init, lint, query, ingest, package metadata, alias skills, documentation contracts, and write-boundary safety.
