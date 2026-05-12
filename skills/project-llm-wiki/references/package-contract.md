# Project LLM Wiki Package Contract

## Source Of Truth

This repository is the working source of truth for the reusable Project LLM Wiki skill package during Phase 1.

Phase 1 does not install into global skill directories.

Future installation may mirror, copy, or symlink the package into a runtime skill directory after this repository proves the package shape and tests.

## Package Boundary

The package owns skills/project-llm-wiki/ and all descendants.

Package-owned files include skill instructions, deterministic helper scripts, wiki templates, reference documents, and tests for the reusable Project LLM Wiki skill.

The package must keep durable project knowledge separate from active task state. `.llm-wiki/` is for curated project knowledge; `.planning/`, Linear, OMX, workflow files, and pull requests are for volatile execution state.

## Non-Goals For Phase 1

Phase 1 does not initialize .llm-wiki/ in target repositories.

Phase 1 does not implement full init, lint, query, ingest, promotion, or AGENTS patch behavior.

Phase 1 does not mutate PeasyDeal repositories, parent workspaces, or the user's global skill directories.

## Future Installation

Later phases can define how this package is installed or mirrored into `~/.codex/skills`, a vault-managed skills directory, or another supported skill runtime.

Any future installation flow must preserve the repo-local source-of-truth contract and avoid writing project wiki content outside the target repository's actual git root.
