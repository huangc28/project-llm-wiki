# vault-wiki-init

`vault-wiki-init` bootstraps the current compounding LLM wiki architecture into an Obsidian vault.

It creates the agent entrypoint, vault schema, note-taking guide, wiki-system project notes, companion skills, an initial `index.md`, and an append-only `log.md`. It also protects any existing target files by asking to back them up as `.bak` before writing.

## Trigger

Use this exact phrase:

`vault wiki init`

## What it creates

- `AGENTS.md` so Codex-class agents know to read `CLAUDE.md`
- `CLAUDE.md` for vault-wide operating rules
- `AI Note-Taking Principles.md` for note-writing rules
- `projects/vault-llm-wiki/overview.md` for the architecture and rationale
- `projects/vault-llm-wiki/usage.md` for trigger phrases and daily workflow
- `index.md` as the orientation map for vault queries
- `log.md` as the append-only history of bootstrap, ingest, query, lint, and reindex operations
- `skills/vault-ingest/SKILL.md`
- `skills/vault-query/SKILL.md`
- `skills/vault-lint/SKILL.md`

## Companion skills

- `vault-ingest`: updates existing notes first, supports `Silent ingest`, `Careful ingest`, `Ingest batch`, daily digest generation, entity pages, and source summary pages
- `vault-query`: answers questions from vault knowledge with `[[wikilink]]` citations and broad-search fallback
- `vault-lint`: runs structural or semantic lint, and supports `Reindex the vault`

## Example result

```text
your-vault/
├── AGENTS.md
├── CLAUDE.md
├── AI Note-Taking Principles.md
├── index.md
├── log.md
├── raw/
├── projects/
│   └── vault-llm-wiki/
│       ├── overview.md
│       └── usage.md
├── daily_notes/
├── Ideas/
└── skills/
    ├── vault-ingest/
    │   └── SKILL.md
    ├── vault-query/
    │   └── SKILL.md
    └── vault-lint/
        └── SKILL.md
```

After setup, Claude Code or Codex can:

- ingest new sources into existing notes instead of scattering new files
- answer questions by reading `index.md` first and citing vault pages
- run lint or reindex passes to keep the wiki coherent over time
