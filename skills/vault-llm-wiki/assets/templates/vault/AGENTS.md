# Agent Instructions

**CRITICAL: All vault-specific operating instructions are in [[CLAUDE.md]]. Read that file before performing any file operations in this vault.**

This vault at `<ABSOLUTE_VAULT_PATH>` is the maintained AI second brain and the primary source of truth for knowledge lookups, prior ingest status, project context, and long-term memory.

When answering questions like "have we ingested this already?", "what do I know about X?", "what did we decide before?", or "what is the current understanding of this topic?", check this vault first.

Use workspace-local memory, chat summaries, or other temporary context only as secondary aids. If they conflict with the vault, prefer the vault unless the user explicitly says otherwise.

See [[CLAUDE.md]] for the full vault schema, directory map, page types, frontmatter conventions, and ingest/query/lint protocols.
