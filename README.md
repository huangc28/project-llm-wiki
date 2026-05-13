# Project LLM Wiki

Project LLM Wiki adds a small, git-tracked `.llm-wiki/` knowledge layer to an existing repository.

Use it when you want future agents and contributors to recover durable project context from the repo itself: architecture notes, decisions, domain concepts, runbooks, feature summaries, and validated implementation learnings.

Keep active task state somewhere else: `.planning/`, Linear, PRs, debug notes, workflow files, or chat history.

## Quick Start

This repo provides the reusable skill package. If it is symlinked into `~/.codex/skills`, open a new Codex session in any target repo and use:

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

## CLI Fallback

You can also call the helper script directly from any existing Git repo.

Preview initialization:

```bash
python3 ~/.codex/skills/project-llm-wiki/scripts/project_wiki.py init --dry-run
```

Create `.llm-wiki/` in the current repo's actual Git root:

```bash
python3 ~/.codex/skills/project-llm-wiki/scripts/project_wiki.py init
```

Lint the wiki:

```bash
python3 ~/.codex/skills/project-llm-wiki/scripts/project_wiki.py lint
```

Prepare a query support packet:

```bash
python3 ~/.codex/skills/project-llm-wiki/scripts/project_wiki.py query "What does the wiki know about onboarding?"
```

Ingest a curated note into an existing page:

```bash
python3 ~/.codex/skills/project-llm-wiki/scripts/project_wiki.py ingest \
  --text "Auth uses JWT access tokens and refresh rotation." \
  --title "Auth implementation note" \
  --target-page architecture/auth \
  --key-idea "Auth uses JWT access tokens and refresh rotation."
```

## Modes

| Mode | Purpose |
| --- | --- |
| `project-wiki-init` | Create the `.llm-wiki/` skeleton in the current Git repo. |
| `project-wiki-lint` | Check wiki structure, broken links, stale notes, unsafe raw material, and repo/wiki drift. |
| `project-wiki-query` | Read `.llm-wiki/index.md` first and answer with repo-local `[[wikilink]]` citations. |
| `project-wiki-ingest` | Add curated source notes to existing pages first; create new pages only with a reason. |

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
