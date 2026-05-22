# Knowledge Layers

Use GSD as the raw execution-memory layer and .llm-wiki as the curated durable-knowledge layer for future agents.

_Updated from Knowledge sedimentation discussion 2026-05-19._

## Update 2026-05-19
Operational workflow: initialize the wiki once, read index.md before non-trivial work, use only relevant linked pages, ingest validated durable learnings after work, then run project-wiki-lint.

_Updated from Knowledge sedimentation workflow discussion 2026-05-19._

## Update 2026-05-19
Agents become operationally smarter from .llm-wiki because the harness supplies durable starting context, not because model weights change.

_Updated from Agent usefulness discussion 2026-05-19._

## Update 2026-05-19
Boundary rule: .planning/ keeps workflow evidence and short-lived progress, while .llm-wiki keeps curated durable project knowledge; repository files win over stale wiki notes.

_Updated from Knowledge boundary discussion 2026-05-19._

## Update 2026-05-21
Daily workflow for knowledge sedimentation:

1. Run `project-wiki-init` once in the target repository. It creates `.llm-wiki/` and writes the root `AGENTS.md` contract.
2. Before non-trivial work, the agent automatically reads `.llm-wiki/index.md`, then only task-relevant linked pages. Simple typo fixes and narrow single-file edits can skip wiki lookup.
3. During work, current repository files and tests remain the source of truth. GitNexus, when available, is navigation support for architecture and relationships, not authority.
4. After validated non-trivial work, the agent automatically proposes 0-3 durable learning candidates instead of writing the wiki directly.
5. Each candidate should include `Learning`, `Evidence`, `Validated by`, and `Decay condition`.
6. The user decides which candidates deserve persistence. Only after approval should the agent run `project-wiki-ingest`.
7. After ingest, run `project-wiki-lint`; commit the wiki update when it is safe and useful.

_Updated from Knowledge sedimentation daily workflow 2026-05-21._
