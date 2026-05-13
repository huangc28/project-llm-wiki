---
name: project-wiki-ingest
description: Ingest curated, de-secreted source notes into a repo-local .llm-wiki/ knowledge layer.
---

# project-wiki-ingest

Thin alias for the `project-wiki-ingest` mode in `project-llm-wiki`.

When invoked:

1. Read the `project-llm-wiki` skill in the same skill root.
2. Ingest only curated, de-secreted source text, file content, or URL provenance paired with curated text.
3. Update existing pages before creating new pages.
4. Create a new page only with an explicit reason.
5. Preserve raw curated notes only when requested and policy-safe.

Never store full transcripts, full logs, dumps, secrets, private data, active task state, execution checkpoints, or large unreviewed raw material.
