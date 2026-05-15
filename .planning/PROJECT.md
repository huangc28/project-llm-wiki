# Project LLM Wiki

## What This Is

Project LLM Wiki is a reusable skill set for creating and maintaining a git-tracked `.llm-wiki/` knowledge layer inside each actual project repository. It adapts the Karpathy LLM Wiki pattern from a personal Obsidian vault into a per-repo operating surface for durable architecture notes, decisions, domain concepts, runbooks, feature summaries, and validated implementation learnings.

The skill should work in multi-repo workspaces by detecting the real git root and initializing `.llm-wiki/` inside the selected repository, not inside a parent folder that only groups projects. The initial rollout target is a single repo such as `peasydeal_be`, then the pattern can be applied to `peasydeal_web`, `peasydeal-product-miner`, and other repos after validation.

## Core Value

Future agents and contributors can recover durable project context from the repository itself without confusing curated project knowledge with volatile task state.

## Requirements

### Validated

- [x] Reusable project wiki skill package with documented project-wiki operations, split references, tests, and a no-dependency helper foundation. Validated in Phase 1.
- [x] Safe git-root `.llm-wiki/` initialization that creates a git-visible skeleton, preserves existing notes on rerun, seeds README/AGENTS source status, and includes raw source policy templates. Validated in Phase 2.
- [x] Deterministic `project-wiki lint` behavior for broken wikilinks, missing index entries, stale pages, secret-looking content, oversized raw files, and likely repo/wiki contradictions. Validated in Phase 3.
- [x] Repo-local query behavior that reads `.llm-wiki/index.md` first, cites wiki pages with wikilinks, and appends query activity to `.llm-wiki/log.md`. Validated in Phase 4.
- [x] Curated ingest behavior that updates existing wiki pages before creating new pages and stores only curated, de-secreted raw sources. Validated in Phase 4.
- [x] Merge-safe root `AGENTS.md` integration for `project-wiki init`, including default patching, dry-run preview, `--no-patch-agents`, marker-bounded updates, byte-preserving unrelated sections, and conflict handling. Validated in Phase 5.
- [x] Dry-run-only validation against `peasydeal_be`, with unchanged target git status, no target `.llm-wiki/`, package test evidence, and a PASS rollout verdict for dry-run-first expansion to `peasydeal_web` and `peasydeal-product-miner`. Validated in Phase 5.

### Active

No active v1 requirements remain after Phase 5 completion.

### Out of Scope

- Replacing Obsidian as the cross-project personal synthesis layer - the repo wiki is intentionally project-local.
- Replacing NotebookLM as an optional retrieval and Q&A layer - NotebookLM may help answer questions, but it is not the repo source of truth.
- Storing active task state, sprint status, execution checkpoints, Linear state, OMX runtime state, or GSD planning state in `.llm-wiki/`.
- Storing secrets, credentials, private customer data, auth tokens, full logs, database exports, or generated large dumps.
- Building a full agent memory database in v1 - `.llm-wiki/` is a human-readable durable knowledge layer, not the whole machine memory substrate.
- Automatically syncing summaries back to Obsidian in v1 - this remains a later design decision.

## Context

This project comes from adapting the existing vault-level LLM Wiki workflow into a repo-native tool. The current vault pattern has three main operations: ingest sources into existing pages, query via `index.md` with wikilink citations, and lint/reindex the knowledge base. The project version should preserve that compounding behavior while respecting repository boundaries and git workflows.

The conceptual split is:

- `.llm-wiki/`: git-tracked durable project knowledge.
- `.planning/`: short-term planning and execution state.
- `WORKFLOW.md`: repo-local workflow contract when present.
- `AGENTS.md`: agent behavior and routing rules.
- NotebookLM: optional retrieval and Q&A over broader curated source material.
- Obsidian vault: cross-project personal synthesis and methodology notes.
- Repo code: source of truth for current implementation.

The first skill set should likely include:

- `project-wiki-init`: detect git root, create `.llm-wiki/` skeleton, seed templates, optionally patch `AGENTS.md`.
- `project-wiki-ingest`: convert curated project sources into durable wiki updates.
- `project-wiki-query`: answer from `.llm-wiki/` with citations and append query logs.
- `project-wiki-lint`: check wiki structure, safety, freshness, and contradictions.
- `project-wiki-promote` or an equivalent later flow: promote validated GSD/PR/debug learnings into `.llm-wiki/`.

## Current State

Phase 5 is complete as of 2026-05-15. The package now exposes the v1 repo-local wiki loop: git-root initialization, lint safety checks, query support packets and logs, curated ingest, and default root `AGENTS.md` integration for future agents.

The Phase 5 rollout verdict is PASS. `project-wiki init --dry-run` was validated from `/Users/huangchihan/develop/bbj/peasydeal/peasydeal_be` without changing that target repo, and next PeasyDeal repos should start with the same dry-run-first procedure from each target git root.

## Constraints

- **Repository boundary**: Initialize inside the actual git root, not a multi-repo parent directory - prevents knowledge from landing in the wrong project.
- **Source of truth**: Trust the current repository over `.llm-wiki/` if they disagree - prevents stale notes from overriding code.
- **Durability boundary**: Store only curated, validated, non-secret knowledge in `.llm-wiki/` - keeps the wiki safe to commit.
- **State boundary**: Keep volatile workflow state in `.planning/`, Linear, OMX, or workflow files - prevents the wiki from becoming noisy and stale.
- **Idempotency**: Re-running init must not duplicate sections or overwrite existing notes - makes the skill safe for repeated use.
- **Merge safety**: Patch `AGENTS.md` with bounded markers or clearly scoped insertion rules - avoids damaging existing instructions such as NotebookLM sections.
- **Simplicity**: Prefer Markdown templates plus small scripts over new dependencies unless a dependency becomes clearly necessary.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use `.llm-wiki/` as the repo wiki path | Clear, explicit, and separate from `.planning/` and docs intended for humans outside the agent workflow | Validated in Phase 2 |
| Keep `.llm-wiki/` git-tracked by default | Durable project knowledge should travel with the repo and be reviewable in diffs | Validated in Phase 2 |
| Keep active task state out of `.llm-wiki/` | Task state changes quickly and belongs in GSD, Linear, OMX, or workflow files | Validated in Phase 2 |
| Keep lint warning-only for safety, freshness, and drift signals | Agents should see unsafe or stale wiki content before rollout without blocking commits on heuristic warnings | Validated in Phase 3 |
| Start with one real repo after a clean test repo | Limits rollout risk before applying the pattern across the PeasyDeal workspace | Validated in Phase 5 with dry-run-only `peasydeal_be` evidence |
| Treat repo code as source of truth over wiki notes | Prevents stale compiled knowledge from becoming authoritative | Validated in Phase 5 root `AGENTS.md` guidance |
| Patch root `AGENTS.md` by default during init with marker-bounded, byte-preserving updates | Agents reliably discover `.llm-wiki/` context without users remembering an extra option, while unrelated instructions remain authoritative | Validated in Phase 5 |
| Apply the next PeasyDeal repos with dry-run-first rollout rules | Prevents parent-workspace writes and makes target repo status evidence auditable before non-dry-run use | Validated in Phase 5 rollout report |
| Keep Obsidian and NotebookLM as adjacent layers | Obsidian handles cross-project synthesis; NotebookLM can support retrieval, but neither replaces repo-local truth | Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `$gsd-transition`):
1. Requirements invalidated? Move to Out of Scope with reason
2. Requirements validated? Move to Validated with phase reference
3. New requirements emerged? Add to Active
4. Decisions to log? Add to Key Decisions
5. "What This Is" still accurate? Update if drifted

**After each milestone** (via `$gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check - still the right priority?
3. Audit Out of Scope - reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-15 after Phase 5 completion*
