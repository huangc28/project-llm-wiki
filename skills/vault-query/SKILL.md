---
name: vault-query
description: Answer questions by synthesizing knowledge from the Obsidian vault wiki. Use when the user asks what they know about a topic, wants a synthesis, or wants connections across notes.
---

# vault-query

Answer a question by synthesizing knowledge from the vault wiki.

## Trigger

User says:
- `"What do I know about X?"`
- `"Synthesize my notes on Y"`
- `"What have I learned about Z?"`
- `"Connect X and Y"` — explicitly find or create bridges between two seemingly unrelated concepts

## Protocol

1. **Read `index.md`** — scan for sections and pages relevant to the question
2. **Read relevant pages** — follow wikilinks as needed for deeper context
3. **Synthesize** — write a structured answer using inline wikilink citations `[[page-name]]`
   - Lead with the direct answer
   - Use mind-map structure (headers, bullets) not long prose
   - Surface contradictions or gaps if found
4. **Offer to file** — if the synthesis reveals a valuable insight not yet in the wiki, offer to create a new concept note
5. **If index has no matches:** fall back to a broad vault search before concluding no coverage
6. **Append to `log.md`**:
   ```
   ## [YYYY-MM-DD] query | <question summary>
   Pages consulted: [[page1]], [[page2]], ...
   Key insight: one-line synthesis
   ```

## Quality Check

- Answer cites specific vault pages with `[[wikilinks]]`
- No fabricated facts — only what is in the vault
- If the vault has no coverage: say so clearly and suggest an ingest

## Related

- [[CLAUDE.md]] — vault schema
- [[index.md]] — always read first
- [[log.md]] — append after every query
