# Phase 5: Agent Instructions and Real Repo Validation - Context

**Gathered:** 2026-05-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 5 adds merge-safe root `AGENTS.md` integration for Project LLM Wiki and validates the complete pattern against a real target repo before broader rollout. It must teach future agents when and how to use `.llm-wiki/` for durable project context without clobbering existing repo instructions or confusing wiki notes with current source-of-truth code.

</domain>

<decisions>
## Implementation Decisions

### AGENTS Patch Timing
- **D-01:** `project-wiki init` patches root `AGENTS.md` by default when safe. The user expects this because users are likely to forget a separate `--patch-agents` option.
- **D-02:** Safe default patching creates root `AGENTS.md` when missing. If root `AGENTS.md` exists and is readable UTF-8, init inserts or updates only the Project LLM Wiki managed section.
- **D-03:** Unsafe root `AGENTS.md` states stop the AGENTS patch path and produce remediation output. Do not guess or repair damaged markers automatically.
- **D-04:** `--dry-run` reports both `.llm-wiki/` skeleton effects and root `AGENTS.md` effects. It must print the exact managed Project LLM Wiki section that would be inserted or updated; a full unified diff is not required.
- **D-05:** Provide an opt-out flag such as `--no-patch-agents` so users can intentionally initialize `.llm-wiki/` without touching root `AGENTS.md`.

### Inserted Rule Wording
- **D-06:** The root `AGENTS.md` section should be short and protocol-oriented, not a full copy of the wiki policy.
- **D-07:** Agents should read `.llm-wiki/index.md` before non-trivial architecture, debugging, product, onboarding, or cross-file implementation work.
- **D-08:** Simple typo fixes and narrow single-file edits do not require wiki lookup.
- **D-09:** Use an index-first, relevant-pages-only lookup: read `.llm-wiki/index.md`, then only task-relevant linked pages. Do not full-scan `.llm-wiki/` by default.
- **D-10:** Agents should update `.llm-wiki/` only after validated non-trivial work produces durable learning. Active task state remains in `.planning/`, issues, PRs, workflow files, or equivalent state systems.
- **D-11:** If `.llm-wiki/` disagrees with current repository files, agents must trust the current repository and report wiki drift so the stale note can be corrected later.

### Marker and Idempotency Contract
- **D-12:** The managed root `AGENTS.md` section uses HTML markers exactly shaped like `<!-- PROJECT-LLM-WIKI:START -->` and `<!-- PROJECT-LLM-WIKI:END -->`.
- **D-13:** When markers already exist, rerunning init updates only the marker-bounded managed section to the current template.
- **D-14:** Marker-external content must remain byte-for-byte unchanged, including NotebookLM, GSD, workflow, and repo-specific instruction sections.
- **D-15:** Treat invalid UTF-8, unmatched start marker, unmatched end marker, or multiple Project LLM Wiki marker pairs as conflicts. Do not patch root `AGENTS.md`; output remediation.
- **D-16:** When root `AGENTS.md` has no Project LLM Wiki markers, append the managed section near the end while preserving the final newline and existing content order.

### Validation and Rollout
- **D-17:** Fixture tests should be preservation-focused. Cover section insertion, section update, dry-run no-write behavior, marker conflicts, and a fixture containing NotebookLM/GSD/workflow sections whose marker-external content remains byte-for-byte unchanged.
- **D-18:** Validate `peasydeal_be` through dry-run reporting only. Phase 5 must not write to or commit `peasydeal_be`.
- **D-19:** The `peasydeal_be` dry-run report must include resolved git root, would-create/would-update paths, the managed root `AGENTS.md` section, and conflict status.
- **D-20:** The final rollout report uses a `PASS` / `FLAG` / `BLOCK` verdict. `PASS` means fixtures, package tests, and `peasydeal_be` dry-run pass. `FLAG` means usable with manual confirmation items. `BLOCK` means conflicts, preservation risk, or test failure.

### the agent's Discretion
The planner may decide exact helper function names, output headings, remediation wording, test fixture filenames, and whether AGENTS patching is implemented inside `init` helpers or factored into dedicated internal functions. Keep the implementation Python standard-library only unless a later phase explicitly changes that constraint.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Scope and Requirements
- `.planning/ROADMAP.md` — Defines Phase 5 goal, plans, and success criteria, including merge-safe `AGENTS.md` integration and `peasydeal_be` dry-run validation.
- `.planning/REQUIREMENTS.md` — Defines AGENT-01 through AGENT-05 and TEST-06 through TEST-07.
- `.planning/PROJECT.md` — Defines the durable wiki purpose, source-of-truth boundary, and target repo rollout context.
- `.planning/STATE.md` — Captures prior decisions and phase history that Phase 5 must preserve.

### Prior Phase Context
- `.planning/phases/02-init-and-wiki-templates/02-CONTEXT.md` — Locks init git-root behavior, idempotency, template skeleton, and existing-file policy.
- `.planning/phases/03-lint-and-safety-checks/03-CONTEXT.md` — Locks lint safety, warning/error semantics, and repo/wiki drift posture.
- `.planning/phases/04-query-and-ingest-loop/04-CONTEXT.md` — Locks query/ingest wiki usage, citation, log, and durable update boundaries.

### Current Implementation and Tests
- `skills/project-llm-wiki/scripts/project_wiki.py` — Existing standard-library helper, init path collection, conflict detection, dry-run output, and file write patterns.
- `skills/project-llm-wiki/assets/templates/llm-wiki/AGENTS.md` — Existing wiki-local agent notes whose root `AGENTS.md` protocol should align with, but not duplicate wholesale.
- `skills/project-llm-wiki/tests/test_project_wiki_init.py` — Existing temporary Git repo subprocess test pattern for init.
- `skills/project-llm-wiki/references/command-surface.md` — Documents AGENTS integration as deferred Phase 5 behavior and must be updated.
- `skills/project-llm-wiki/references/testing.md` — Documents validation contracts and should receive Phase 5 test coverage notes.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `resolve_git_root`, `find_candidate_child_repos`, `find_init_conflicts`, `collect_init_paths`, and `apply_init_plan` in `skills/project-llm-wiki/scripts/project_wiki.py` provide the current init control flow that AGENTS patching should extend without changing repository-boundary behavior.
- `create_file_if_missing` and current conflict preflight patterns show the preferred idempotent write shape.
- The temporary Git repo subprocess helpers in `test_project_wiki_init.py` are the expected fixture style for AGENTS patch tests.

### Established Patterns
- Helper implementation is Python standard library only.
- Tests invoke the helper through subprocesses against temporary Git repositories.
- Existing init is conservative: it preflights conflicts before writes, preserves existing wiki files, and reports skipped paths.
- Current `.llm-wiki/AGENTS.md` already contains the core wiki-read and trust-boundary wording, but root `AGENTS.md` needs a shorter repository-wide retrieval protocol.

### Integration Points
- Extend `project_wiki.py init` parser and `run_init` output for default AGENTS patching, `--no-patch-agents`, and dry-run managed section display.
- Add root `AGENTS.md` managed-section helpers that can be tested independently through the existing init subprocess boundary.
- Update documentation references and package tests so command surface and testing docs no longer describe AGENTS integration as deferred.

</code_context>

<specifics>
## Specific Ideas

- The user explicitly rejected hiding root `AGENTS.md` integration behind an easy-to-forget `--patch-agents` option.
- The root `AGENTS.md` section should be concise enough that it improves agent startup behavior without becoming another large policy document.
- The managed section should say, in substance: before non-trivial architecture, debugging, product, onboarding, or cross-file implementation work, read `.llm-wiki/index.md` first, then only relevant linked pages; trust repo files over wiki notes; update the wiki only after validated durable work.
- `peasydeal_be` is the first real target repo for smoke validation, not the source repo for the reusable package.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within Phase 5 scope.

</deferred>

---

*Phase: 5-Agent Instructions and Real Repo Validation*
*Context gathered: 2026-05-14*
