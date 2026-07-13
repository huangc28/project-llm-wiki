---
name: vault-ghost
description: Answer a question or draft a response the way the user would, based on their writing style, opinions, and thinking patterns in the Obsidian vault. Use when the user wants to know "what would I think about X" or wants a draft that sounds like them.
---

# Vault Ghost

Answer a question or draft content in the user's voice, based on patterns in their vault.

## Steps

1. Identify the question or topic to answer (from user input).
2. Use Obsidian MCP to read relevant notes — especially daily notes, project notes, and any opinion pieces.
3. Extract the user's:
   - Characteristic vocabulary and sentence structure
   - Typical reasoning style (do they list things? Think in tradeoffs? Tell stories?)
   - Known positions on related topics
   - Values and priorities that show up repeatedly
4. Draft a response that sounds like the user wrote it — not like an AI.
5. Stay true to what the vault reveals. Do not invent opinions not supported by vault evidence.

## Output Format

- The response, written in the user's voice
- Brief note at the end: "Based on: [which notes / patterns informed this]"
- If the vault doesn't have enough signal: say so and ask the user to share more context
