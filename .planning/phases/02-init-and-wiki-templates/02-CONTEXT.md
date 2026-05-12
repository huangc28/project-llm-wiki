# Phase 2: Init and Wiki Templates - Context

**Gathered:** 2026-05-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 2 implements `project-wiki-init` for a single actual git repository. It must safely create an idempotent `.llm-wiki/` skeleton, seed minimal human-doc based starting knowledge, and install raw-source policy templates. It does not implement lint scanning, query/ingest behavior, AGENTS patching, cross-repo querying, or shared-wiki orchestration.

</domain>

<decisions>
## Implementation Decisions

### Git-root and Safety Behavior
- **D-01:** `project-wiki-init` must resolve the actual repository root with `git rev-parse --show-toplevel`; when run from a subdirectory, it creates `.llm-wiki/` at the resolved git root, not the current directory.
- **D-02:** If init is run from a multi-repo parent or another non-target workspace, it must not write. It may list candidate child git repos when discoverable, then tell the user to `cd` into the intended repo before running init.
- **D-03:** Phase 2 does not support `--target`. Explicit target selection is deferred; this phase only initializes the current actual repo.
- **D-04:** Successful and failed output should be concise: resolved git root, created paths, skipped paths, conflicts when present, and the next useful command.
- **D-05:** Shared FE/BE knowledge is not represented by writing `.llm-wiki/` into a workspace parent. Each code repo keeps its own `.llm-wiki/`; shared cross-repo context belongs in a dedicated shared repo such as `peasydeal-context/.llm-wiki/`.

### Template Skeleton Shape
- **D-06:** The initial skeleton should be minimal but complete: required landing pages plus the planned category directories, without excessive starter content.
- **D-07:** Create these initial files and directories: `README.md`, `AGENTS.md`, `index.md`, `log.md`, `raw/README.md`, `raw/curated/README.md`, `architecture/`, `domain/`, `decisions/`, `operations/`, `features/`, `summaries/`, and `raw/curated/`.
- **D-08:** Add `.gitkeep` to otherwise-empty category directories so the complete skeleton appears in `git status`.
- **D-09:** Add `.llm-wiki/features/ideas.md` and link it from `index.md`. This page is for durable but immature ideas; it is not a roadmap, backlog, or active task-state store.
- **D-10:** Initial pages should be short guidance templates: purpose, what belongs there, what does not belong there, and a few example links.
- **D-11:** The skeleton is a stable default, not a permanent schema. Future structure changes should be additive or migration-based and must not overwrite existing notes.

### Seeding From Existing Repo Files
- **D-12:** Seed with light summary plus provenance only. Do not attempt deep interpretation during init.
- **D-13:** Phase 2 may read only `README.md` and `AGENTS.md` for seed content. These are human-authored orientation/instruction files.
- **D-14:** Do not seed wiki content from language manifests or config files such as `package.json`, `pyproject.toml`, `go.mod`, or `Cargo.toml`. Future agents should read current repo files directly when they need tech-stack facts.
- **D-15:** Write seeded content to `.llm-wiki/summaries/repo-overview.md` and link it from `index.md`.
- **D-16:** If `README.md` or `AGENTS.md` is missing, init should still create the skeleton and report the source as skipped.

### Idempotency and Existing-file Policy
- **D-17:** Re-running init must never overwrite existing files. It only creates missing files/directories and reports skipped paths.
- **D-18:** If an existing `.llm-wiki/index.md` is missing links to new default pages, init must not edit it. It should report missing links in output so the user can update manually.
- **D-19:** If a required directory path is occupied by a file, init must fail before partial writes and list each conflict with the expected path type.
- **D-20:** Support `--dry-run`; it reports would-create, would-skip, and conflicts without writing files.

### Raw Source Policy
- **D-21:** `.llm-wiki/raw/README.md` should use a strict allow/deny policy.
- **D-22:** Raw policy must explicitly forbid secrets, credentials, auth tokens, private customer data, full logs, database exports, generated dumps, and other unsafe material.
- **D-23:** Create `.llm-wiki/raw/curated/README.md` explaining that curated raw sources must be de-secreted, intentionally selected, and small sources or excerpts.
- **D-24:** Init does not perform secret scanning. Deterministic secret and safety checks belong to Phase 3 lint.
- **D-25:** Use a light naming convention for curated raw files, such as date or source-name based filenames (`2026-05-13-api-notes.md`), but do not enforce naming in Phase 2.

### the agent's Discretion
The planner may decide exact function boundaries, test fixture names, template wording, and output formatting details as long as the decisions above remain true and the implementation stays standard-library only.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project and Requirements
- `.planning/PROJECT.md` — Defines the repo-local wiki concept, source-of-truth model, boundaries, and out-of-scope items.
- `.planning/REQUIREMENTS.md` — Defines Phase 2 requirements `INIT-01` through `INIT-06`, `RAW-01` through `RAW-03`, `TEST-01`, and `TEST-02`.
- `.planning/ROADMAP.md` — Defines Phase 2 goal, success criteria, and planned work slices.
- `.planning/STATE.md` — Contains recent decisions from Phase 1 and current project position.

### Package Surface
- `README.md` — Root project/package overview and validation command.
- `skills/project-llm-wiki/SKILL.md` — Skill triggers, safety boundaries, and mode descriptions.
- `skills/project-llm-wiki/references/command-surface.md` — Planned command modes and later phase ownership.
- `skills/project-llm-wiki/references/package-contract.md` — Package ownership and repo-local source-of-truth contract.
- `skills/project-llm-wiki/references/testing.md` — Test command and no-dependency rule.
- `skills/project-llm-wiki/assets/templates/README.md` — Phase 2 template ownership and safety rules.

### Current Implementation and Tests
- `skills/project-llm-wiki/scripts/project_wiki.py` — Current helper skeleton that Phase 2 extends for init behavior.
- `skills/project-llm-wiki/tests/test_project_wiki_package.py` — Current baseline tests to extend with init and fixture coverage.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `skills/project-llm-wiki/scripts/project_wiki.py`: Existing argparse command surface; Phase 2 should replace the planned `init` handler with real init behavior while leaving lint/query/ingest planned.
- `skills/project-llm-wiki/assets/templates/`: Stable location for `.llm-wiki/` template assets.
- `skills/project-llm-wiki/tests/test_project_wiki_package.py`: Existing unittest pattern for subprocess-level helper behavior and import whitelist checks.

### Established Patterns
- Implementation currently uses Python standard library only.
- Tests use `unittest`, `subprocess`, `sys`, and `pathlib`; continue this style.
- The package keeps behavior split across skill instructions, references, scripts, templates, and tests rather than a single monolithic prompt.

### Integration Points
- The `init` subcommand in `project_wiki.py` is the Phase 2 entrypoint.
- Template files belong under `skills/project-llm-wiki/assets/templates/`.
- Clean-repo/idempotency fixture tests should live under `skills/project-llm-wiki/tests/` unless the plan introduces a clearer fixture subdirectory.

</code_context>

<specifics>
## Specific Ideas

- Use a dedicated shared repo, not a workspace parent folder, for shared FE/BE knowledge.
- `features/ideas.md` should let users quickly capture later ideas with fields like thought, why it might matter, current leaning, not decided, and related links.
- The wiki should remember durable ideas through `index.md` links, but should not become a task inbox.
- Keep seeding human-doc based. The user explicitly rejected turning programming-language manifests into wiki seed sources.

</specifics>

<deferred>
## Deferred Ideas

- Support explicit cross-repo querying across repo-local wikis and a dedicated shared wiki after the single-repo workflow is proven.
- Support explicit target selection such as `--target path/to/repo` in a later phase if the parent-workspace workflow proves necessary.

</deferred>

---

*Phase: 2-Init and Wiki Templates*
*Context gathered: 2026-05-13*
