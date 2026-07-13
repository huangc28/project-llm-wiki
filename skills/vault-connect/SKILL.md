---
name: vault-connect
description: Bridge two seemingly unrelated domains or topics from the Obsidian vault. Surfaces unexpected connections between areas of the user's knowledge and life.
---

# Vault Connect

Find unexpected connections between two domains using the user's vault as the link graph.

## Steps

1. Ask the user for two topics/domains to connect (if not already provided).
2. Use Obsidian MCP to search both topics across the vault.
3. Look for:
   - Notes that reference both topics
   - Shared tags or wikilinks between the two domains
   - Structural similarities in how the user thinks about each
   - A third concept that links them
4. Do NOT force a connection. If there isn't a meaningful one, say so and suggest what's needed to build one.

## Output Format

- The bridge: what concept/pattern connects the two domains
- Evidence from the vault (specific notes, not just topic names)
- A concrete idea or action that emerges from the connection
- Optional: a new note worth creating to capture this link
