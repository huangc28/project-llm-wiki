# Project LLM Wiki Templates

## Inventory

This directory contains the inspectable default template assets used by `project-wiki init`.

- `llm-wiki/README.md` - wiki purpose and durable knowledge boundaries.
- `llm-wiki/AGENTS.md` - agent-facing rules for reading and trusting the wiki.
- `llm-wiki/index.md` - default navigation across wiki categories.
- `llm-wiki/log.md` - durable query and update log guidance.
- `llm-wiki/raw/README.md` - raw source allow/deny policy.
- `llm-wiki/raw/curated/README.md` - curated raw source requirements.
- `llm-wiki/features/ideas.md` - durable idea capture page.

## Ownership

The Project LLM Wiki package owns these default `.llm-wiki/` skeleton templates, idempotent init behavior, and raw source policy files.

Template changes must stay inside the Project LLM Wiki package boundary unless a later plan explicitly adds target repository initialization behavior.

## Template Safety Rules

Templates must not contain secrets, customer data, logs, database exports, or generated dumps.

Templates must preserve the rule that current repo code wins over wiki notes.

Templates must keep durable project knowledge separate from `.planning/`, Linear, OMX, workflow files, pull requests, and other volatile task state.
