# Vault LLM Wiki Templates

## Inventory

The `vault/` subdirectory is the single maintained source for the in-vault
control-file templates the `vault-llm-wiki` core installs when bootstrapping an
Obsidian vault. This `README.md` is maintainer documentation only — it is not a
control file and must not be installed into a vault.

- `vault/AGENTS.md` — Codex entrypoint that points agents to `CLAUDE.md`.
- `vault/CLAUDE.md` — vault schema, directory map, page types, frontmatter, and
  the ingest/query/lint operating contract.
- `vault/AI Note-Taking Principles.md` — mind-map note style guide.
- `vault/index.md` — seeded catalog of wiki pages; read first on every query.
- `vault/log.md` — append-only operation log.

## Ownership

The `vault-llm-wiki` core owns these control-file templates as the single source.
Previously they were hand-inlined inside the `vault-wiki-init` skill; keep any
change here so the bootstrap and the core never drift apart.

Placeholders (`<ABSOLUTE_VAULT_PATH>`, `<TODAY>`, `<TOTAL_PAGES>`, and the
`index.md` / `log.md` substitution tokens) are filled in at bootstrap time.

## Template Safety Rules

Templates must not contain secrets, customer data, logs, database exports, or
generated dumps.

Templates must preserve the source-of-truth rule: the maintained vault wins over
transient workspace memory or chat summaries when they conflict.

Templates must keep durable knowledge separate from active task state — never seed
full transcripts, full logs, or unvalidated notes into a vault.
