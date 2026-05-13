# Phase 5: Agent Instructions and Real Repo Validation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-14
**Phase:** 5-Agent Instructions and Real Repo Validation
**Areas discussed:** AGENTS patch timing, Inserted rule wording, Marker and idempotency contract, Validation and rollout shape

---

## AGENTS Patch Timing

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit flag writes | `project-wiki init` creates `.llm-wiki/` and only patches root `AGENTS.md` with an explicit flag such as `--patch-agents`. | |
| Default writes when safe | `project-wiki init` patches root `AGENTS.md` by default when safety checks pass. | ✓ |
| Never in init | Init never patches root `AGENTS.md`; use a separate command. | |

**User's choice:** Default writes when safe.
**Notes:** The user said a `--patch-agents` option would likely be forgotten, so root `AGENTS.md` integration should be part of the default safe init behavior. Follow-up decisions locked safe create-or-patch behavior, `--dry-run` managed-section display, and an opt-out flag.

---

## Inserted Rule Wording

| Option | Description | Selected |
|--------|-------------|----------|
| Non-trivial domains | Read `.llm-wiki/index.md` before non-trivial architecture, debugging, product, onboarding, or cross-file implementation work. | ✓ |
| Every coding task | Read `.llm-wiki/index.md` before every coding task. | |
| Only when user asks wiki/project context | Read the wiki only when the user explicitly asks. | |

**User's choice:** Non-trivial domains.
**Notes:** Follow-up decisions locked index-first relevant-page lookup, durable-update-only wiki writes, and repo-code authority with wiki drift reporting.

---

## Marker and Idempotency Contract

| Option | Description | Selected |
|--------|-------------|----------|
| HTML markers | Use `<!-- PROJECT-LLM-WIKI:START -->` and `<!-- PROJECT-LLM-WIKI:END -->`. | ✓ |
| Markdown heading only | Use a heading as the section boundary. | |
| HTML markers plus heading | Use markers around a visible heading. | |

**User's choice:** HTML markers.
**Notes:** Follow-up decisions locked current-template replacement inside the managed section, byte-for-byte preservation outside markers, strict marker conflict handling, and append-near-end insertion when no marker exists.

---

## Validation and Rollout Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Preservation-focused fixtures | Cover insert, update, dry-run, conflicts, and marker-external preservation for NotebookLM/GSD/workflow sections. | ✓ |
| Only happy path | Cover only insert/update happy paths. | |
| Exhaustive fixture matrix | Test many AGENTS.md variants and insertion positions. | |

**User's choice:** Preservation-focused fixtures.
**Notes:** Follow-up decisions locked `peasydeal_be` dry-run report only and a final `PASS` / `FLAG` / `BLOCK` rollout verdict.

---

## the agent's Discretion

- Exact helper function names.
- Exact output headings and remediation wording.
- Test fixture filenames and organization.
- Internal factoring between `run_init` and AGENTS patch helper functions.

## Deferred Ideas

None.
