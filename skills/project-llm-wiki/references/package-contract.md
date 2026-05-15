# Project LLM Wiki Package Contract

## Source Of Truth

This repository is the working source of truth for the reusable Project LLM Wiki skill package.

Phase 1 did not install into global skill directories.

Phase 6 adds a Codex skill installer that symlinks the package-owned skills into `${CODEX_HOME:-~/.codex}/skills` or an explicit `--target` directory.

The installer only manages skill symlinks. It does not initialize `.llm-wiki/`, does not patch project `AGENTS.md`, and does not mutate target repositories.

## Package Boundary

The package owns skills/project-llm-wiki/ and all descendants.

Package-owned files include skill instructions, deterministic helper scripts, wiki templates, reference documents, and tests for the reusable Project LLM Wiki skill.

The package must keep durable project knowledge separate from active task state. `.llm-wiki/` is for curated project knowledge; `.planning/`, Linear, OMX, workflow files, and pull requests are for volatile execution state.

## Non-Goals For Install

Install does not initialize .llm-wiki/ in target repositories.

Install does not implement repo-local init, lint, query, ingest, promotion, or AGENTS patch behavior. Those remain separate helper modes and must run from the intended target repository.

Install does not mutate PeasyDeal repositories, parent workspaces, or any project repository.

## Installation Boundary

`project-wiki install` may create, skip, replace, or remove package-owned symlinks in a Codex skills directory.

It must preserve the repo-local source-of-truth contract and avoid writing project wiki content outside the target repository's actual git root.
