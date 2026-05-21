# Project LLM Wiki Log

Use this page for durable wiki maintenance notes and query history that should remain useful after the current task ends.

Active task state belongs outside `.llm-wiki/` in planning tools, issue trackers, workflow state, or commits.

## Entries

- YYYY-MM-DD: Add durable wiki updates here with links to changed pages.

## [2026-05-19] ingest | Knowledge sedimentation discussion
- Pages touched: [[architecture/knowledge-layers]]
- Key insight: Use GSD as the raw execution-memory layer and .llm-wiki as the curated durable-knowledge layer for future agents.

## [2026-05-19] ingest | Knowledge sedimentation workflow discussion
- Pages touched: [[architecture/knowledge-layers]]
- Key insight: Operational workflow: initialize the wiki once, read index.md before non-trivial work, use only relevant linked pages, ingest validated durable learnings after work, then run project-wiki-lint.

## [2026-05-19] ingest | Agent usefulness discussion
- Pages touched: [[architecture/knowledge-layers]]
- Key insight: Agents become operationally smarter from .llm-wiki because the harness supplies durable starting context, not because model weights change.

## [2026-05-19] ingest | Knowledge boundary discussion
- Pages touched: [[architecture/knowledge-layers]]
- Key insight: Boundary rule: .planning/ keeps workflow evidence and short-lived progress, while .llm-wiki keeps curated durable project knowledge; repository files win over stale wiki notes.
