# Phase 4: Query and Ingest Loop - Context

**Gathered:** 2026-05-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 4 implements the repo-local compounding wiki loop for `.llm-wiki/`: query answers that read `index.md` first, cite repo-local wiki pages, and append concise query history; plus ingest behavior that turns curated sources into durable wiki updates by updating existing pages first. It does not implement AGENTS.md patching, real-repo rollout validation, global Obsidian sync, NotebookLM integration, vector search, or a mandatory video-analysis dependency.

</domain>

<decisions>
## Implementation Decisions

### Query Answer Contract
- **D-01:** Query answers are evidence-first. Direct claims need `[[wikilink]]` support from `.llm-wiki/` pages.
- **D-02:** Synthesis and inference are allowed only in a clearly labeled inference section. The answer must distinguish direct wiki-supported claims from inferred connections.
- **D-03:** Unsupported topics return a clear not-covered answer instead of guessing.

### Query Not-Covered Behavior
- **D-04:** A not-covered answer should say that `.llm-wiki/` does not currently cover the topic, list pages consulted, and suggest what type of source should be ingested next.
- **D-05:** Do not generate a full ingest draft during query. Keep the response conservative and route source-gathering to ingest.

### Query Execution Shape
- **D-06:** `project-wiki query` is agent-protocol-first. The skill instructs the agent to read `.llm-wiki/index.md`, inspect relevant pages, answer with citations, and append the log.
- **D-07:** The Python helper may provide auxiliary validation, discovery, or formatting support, but Phase 4 should not hard-code answer generation into deterministic Python logic.

### Query Log Shape
- **D-08:** Every query appends a concise `log.md` entry with date, query summary, consulted pages, and key insight or not-covered result.
- **D-09:** Do not store complete question/answer transcripts in `log.md`; the log is an operational timeline, not chat history.

### Ingest Source Inputs
- **D-10:** Ingest supports text, file, and URL sources.
- **D-11:** URL ingest remains subject to raw policy. It must not store unsafe, uncurated, secret-bearing, private, or oversized source material.
- **D-12:** Video sources, including YouTube, must be preprocessed into curated text before core ingest. `$watch-video` may be used by this user as a local preprocessing workflow, but Project LLM Wiki core ingest must not depend on that personal skill.
- **D-13:** If a user provides only a video URL and no adapter is available, ingest should ask for a transcript, summary, or curated notes. If an adapter is available, its output is treated as curated source material, not an authoritative full transcript.

### Raw Curated Copy Policy
- **D-14:** Ingest always updates compiled wiki pages first. `.llm-wiki/raw/curated/` is a source layer, not a dump bucket.
- **D-15:** Preserve a curated source note in `.llm-wiki/raw/curated/` only when the source material is short, important, unstable, user-provided, adapter-generated, or likely needed for future verification.
- **D-16:** Stable external URLs may be stored as provenance only.
- **D-17:** Never store full transcripts, full logs, dumps, secrets, private data, or large unreviewed raw material.

### Existing-Page Update Rules
- **D-18:** Ingest updates existing pages before creating new pages.
- **D-19:** Use a source-size-based blast radius: small or narrow sources update 1-3 pages; cross-cutting sources may update 5-10 pages; hard cap is 15 pages.
- **D-20:** Create a new page only when no existing page covers the concept, or when a concept is referenced across multiple pages and deserves its own durable page.

### Provenance, Index, and Log Updates
- **D-21:** Every touched page gets a concise provenance note such as `Updated from ... YYYY-MM-DD`.
- **D-22:** `log.md` records pages touched and key ideas for each ingest.
- **D-23:** `index.md` is updated for newly created pages, not for every edit to an already indexed page.

### the agent's Discretion
The planner may decide exact command flags, helper function boundaries, source title normalization, provenance line wording, URL fetch adapter shape, and test fixture names. Keep the implementation standard-library only unless a later phase explicitly changes that constraint.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project and Requirements
- `.planning/PROJECT.md` — Defines the repo-local wiki concept, durable/volatile boundary, and Phase 4 current state.
- `.planning/REQUIREMENTS.md` — Defines Phase 4 requirements `QUERY-01` through `QUERY-04`, `INGEST-01` through `INGEST-05`, and `TEST-03`.
- `.planning/ROADMAP.md` — Defines Phase 4 goal, success criteria, and planned work slices.
- `.planning/STATE.md` — Records Phase 4 as the current phase and carries prior decisions.

### Prior Phase Context
- `.planning/phases/03-lint-and-safety-checks/03-CONTEXT.md` — Locked lint decisions, especially read-only behavior, warning/error semantics, and raw safety boundaries.
- `.planning/phases/02-init-and-wiki-templates/02-CONTEXT.md` — Locked init and template decisions, including raw policy, Obsidian wikilinks, and `.llm-wiki/` skeleton shape.

### Package Surface and Templates
- `skills/project-llm-wiki/scripts/project_wiki.py` — Current helper implementation; query and ingest are still planned Phase 4 commands.
- `skills/project-llm-wiki/references/command-surface.md` — Documents planned query and ingest behavior.
- `skills/project-llm-wiki/references/testing.md` — Current unittest command and validation style.
- `skills/project-llm-wiki/assets/templates/llm-wiki/index.md` — Default index shape and category navigation.
- `skills/project-llm-wiki/assets/templates/llm-wiki/log.md` — Default log structure and intended operation-history role.
- `skills/project-llm-wiki/assets/templates/llm-wiki/raw/README.md` — Raw source allow/deny policy.
- `skills/project-llm-wiki/assets/templates/llm-wiki/raw/curated/README.md` — Curated raw source requirements.

### Methodology References
- `/Users/huangchihan/Documents/markdowns/projects/vault-llm-wiki/overview.md` — User's vault-level Karpathy LLM Wiki adaptation; defines raw/wiki/schema layers and compounding behavior.
- `/Users/huangchihan/Documents/markdowns/projects/vault-llm-wiki/usage.md` — User's day-to-day vault workflow; defines ingest/query/log/index behavior and blast-radius patterns.
- `/Users/huangchihan/Documents/markdowns/skills/vault-ingest/SKILL.md` — Existing vault ingest protocol: update existing pages first, add provenance, log, update index, create summaries only for cross-cutting sources.
- `https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f` — Karpathy LLM Wiki pattern; raw sources, compiled wiki, schema, ingest, query, lint, index, and log concepts.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `skills/project-llm-wiki/scripts/project_wiki.py`: Existing argparse surface, Git-root resolver, wiki path constants, read helpers, lint renderers, and planned `query`/`ingest` subcommands.
- `skills/project-llm-wiki/tests/test_project_wiki_init.py`: Temporary Git repo fixture style and subprocess helper pattern for `.llm-wiki/` behavior.
- `skills/project-llm-wiki/tests/test_project_wiki_lint.py`: Subprocess-level wiki mutation fixtures and read-only snapshot assertions that Phase 4 can reuse for query/ingest behavior.
- `skills/project-llm-wiki/tests/test_project_wiki_package.py`: Package/import/help/doc tests and stdlib import whitelist.
- `.llm-wiki` templates under `skills/project-llm-wiki/assets/templates/llm-wiki/`: index, log, raw policy, and starter pages that define the user-facing wiki surface.

### Established Patterns
- Implementation is Python standard library only.
- Tests use `unittest` and subprocess-level assertions through the same helper script users run.
- The package keeps behavior split across `SKILL.md`, references, scripts, templates, and tests rather than one monolithic prompt.
- Prior phases use Git-root resolution before reading or writing `.llm-wiki/`; Phase 4 should preserve that repository boundary.
- Lint is read-only. Ingest is allowed to write `.llm-wiki/`, but should keep active task state outside the wiki.

### Integration Points
- Replace the planned `query` handler in `project_wiki.py` with either protocol-support behavior or a useful helper surface without making Python generate final LLM answers.
- Replace the planned `ingest` handler in `project_wiki.py` with behavior that supports curated text/file/URL inputs and safe wiki updates.
- Update `references/command-surface.md` and `references/testing.md` to describe the Phase 4 query/ingest contract.
- Add tests for query fixture output/log append behavior and ingest boundary behavior under `skills/project-llm-wiki/tests/`.

</code_context>

<specifics>
## Specific Ideas

- The user wants the repo-local LLM Wiki to follow Karpathy's compounding model: raw sources are curated source material, wiki pages are the compiled layer, and schema/AGENTS instructions define how agents operate.
- The user may personally use `$watch-video` to preprocess YouTube links, but third-party users will not have that personal skill. Core ingest must remain adapter-agnostic.
- YouTube/video ingest should preserve curated notes, useful timestamps, and provenance, not full transcripts.
- Query and ingest should both update `log.md`, but keep entries concise and parseable.
- The key signal for ingest success is that existing wiki pages get richer, not that a new isolated note was created.

</specifics>

<deferred>
## Deferred Ideas

- A future optional video-analysis adapter can standardize YouTube preprocessing, but Phase 4 core ingest should stay adapter-agnostic.
- A future dedicated raw-source verification mode may help decide which curated excerpts should be retained long-term.
- Embedding/vector search or qmd-style search can be added later if the index stops being enough.

</deferred>

---

*Phase: 4-Query and Ingest Loop*
*Context gathered: 2026-05-13*
