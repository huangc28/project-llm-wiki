---
name: project-wiki-query
description: Answer from a repo-local .llm-wiki/ using index-first lookup and [[wikilink]] citations.
---

# project-wiki-query

Thin alias for the `project-wiki-query` mode in `project-llm-wiki`.

When invoked:

1. Read the `project-llm-wiki` skill in the same skill root.
2. Read `.llm-wiki/index.md` first in the target repository.
3. Inspect relevant linked wiki pages before answering.
4. Cite direct claims with repo-local `[[wikilink]]` citations.
5. Put synthesis under an `Inference` section.
6. If the wiki does not cover the topic, say so, list pages consulted, and suggest what source to ingest next.

Append only concise query learnings to `.llm-wiki/log.md`; never store full chat transcripts.
