# Phase 2: Init and Wiki Templates - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-13
**Phase:** 2-Init and Wiki Templates
**Areas discussed:** Git-root and safety behavior, Template skeleton shape, Seeding from existing repo files, Idempotency and existing-file policy, Raw source policy strictness

---

## Git-root and Safety Behavior

| Decision Point | Options Presented | Selected |
|---|---|---|
| Init target from subdirectory | Use git root; Use cwd; Require flag; Other | Use git root |
| Multi-repo parent behavior | Fail with guidance; Suggest child repos; Require `--target`; Other | Suggest child repos without writing |
| Shared FE/BE context | Repo-local only; Dedicated shared repo; Workspace parent wiki; Other | Dedicated shared repo |
| `--target` support | No `--target` for now; Support `--target`; Dry-run only target; Other | No `--target` for now |
| Output detail | Concise paths + actions; Very quiet; Verbose report; Other | Concise paths + actions |

**Notes:** The user clarified that FE/BE repos may share context. The locked model is per-repo `.llm-wiki/` for code truth plus an optional dedicated shared context repo for cross-repo domain/product/API knowledge.

---

## Template Skeleton Shape

| Decision Point | Options Presented | Selected |
|---|---|---|
| Skeleton style | Minimal but complete; Rich starter wiki; Directory only; Other | Minimal but complete |
| Idea memory | No idea page; Feature ideas page; Backlog-like page; Other | Feature ideas page |
| Category directories | Create all upfront; Create only when needed; Create with `.gitkeep`; Other | Create all upfront |
| Empty directory tracking | Yes, add `.gitkeep`; No `.gitkeep`; Use README instead; Other | Yes, add `.gitkeep` |
| Initial page detail | Short guidance templates; Detailed writing templates; Almost empty pages; Other | Short guidance templates |
| Future evolution | Permanent schema; Default skeleton; Migration-based evolution; Other | Default skeleton with additive/migration changes |

**Notes:** The user asked whether future structure changes remain possible. The answer captured in context is yes: Phase 2 provides a default skeleton, not a permanent schema.

---

## Seeding from Existing Repo Files

| Decision Point | Options Presented | Selected |
|---|---|---|
| Seeding depth | Light summary + provenance; Structured extraction; Provenance only; Other | Light summary + provenance |
| Language manifests | Use manifests for orientation; Do not seed from manifests; Only record manifest paths; Other | Do not seed from manifests |
| Seed sources | README + AGENTS only; README + AGENTS + docs/ADR; All common project files; Other | README + AGENTS only |
| Seed output location | README summary page; Split by topic; Only index notes; Other | `.llm-wiki/summaries/repo-overview.md` |
| Missing seed files | Skip gracefully; Create placeholder summary; Fail init; Other | Skip gracefully |

**Notes:** The user challenged why files like `pyproject.toml` and `go.mod` would be considered. The resulting decision is that Phase 2 should not mirror programming-language manifests or configs into wiki seed content.

---

## Idempotency and Existing-file Policy

| Decision Point | Options Presented | Selected |
|---|---|---|
| Existing files | Never overwrite; Marker merge; Prompt before overwrite; Other | Never overwrite |
| Existing index missing links | Do not edit existing index; Append missing links; Marker-bounded section; Other | Do not edit existing index |
| Path type conflict | Fail with conflict list; Skip conflict paths; Rename existing file; Other | Fail with conflict list |
| Dry run | Yes; No; Only on conflict; Other | Yes |

**Notes:** The user preferred the simplest safe rule: init creates missing pieces, reports skipped paths, and never rewrites user-owned wiki notes.

---

## Raw Source Policy Strictness

| Decision Point | Options Presented | Selected |
|---|---|---|
| Raw policy tone | Strict allow/deny policy; Guidance only; Minimal warning; Other | Strict allow/deny policy |
| Curated raw README | Yes; No; Use `.gitkeep` only; Other | Yes |
| Init-time secret scan | No scan in init; Scan raw only; Scan whole wiki; Other | No scan in init |
| Raw filename convention | Light convention; Strict naming; No convention; Other | Light convention |

**Notes:** Policy is strict, but enforcement is intentionally delayed to Phase 3 lint.

---

## the agent's Discretion

- Exact helper function boundaries.
- Exact template wording.
- Fixture directory layout.
- Output table/list formatting, as long as resolved root, created/skipped paths, conflicts, and next command are visible.

## Deferred Ideas

- Cross-repo querying across repo-local wikis plus a dedicated shared wiki.
- Later `--target` support for parent-workspace workflows.
