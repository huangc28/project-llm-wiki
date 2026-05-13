# Phase 3: Lint and Safety Checks - Context

**Gathered:** 2026-05-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 3 implements deterministic `project-wiki lint` behavior for a repo-local `.llm-wiki/`. It should make unsafe, stale, missing, or broken wiki content visible before rollout. It does not implement query, ingest, AGENTS patching, semantic AI contradiction detection, or automatic fixes.

</domain>

<decisions>
## Implementation Decisions

### Wikilink and Index Rules
- **D-01:** Lint should check only Obsidian-style `[[wikilink]]` links in Phase 3, not general Markdown links.
- **D-02:** Lint should support common Obsidian forms for page existence checks: `[[path]]`, `[[path.md]]`, `[[path|Alias]]`, and `[[path#Heading]]`.
- **D-03:** Alias text and heading fragments are ignored in Phase 3. Lint verifies that the linked page exists, but it does not validate that a heading exists.
- **D-04:** Broken wikilinks are `error` findings because they break Obsidian navigation.
- **D-05:** Main wiki pages should be discoverable from `.llm-wiki/index.md`. Missing index coverage for main wiki pages is a `warning`.
- **D-06:** `raw/curated/` source files are not required to be listed in `index.md`.
- **D-07:** A brand-new standalone topic page is not required to contain outgoing links. Lint should not force every page to link elsewhere.

### Safety and Size Heuristics
- **D-08:** Secret-looking content detection should use high-confidence patterns only, to avoid noisy false positives in documentation.
- **D-09:** Secret-looking detection scans the entire `.llm-wiki/`, because secrets should not appear in any wiki page.
- **D-10:** Secret-looking findings are `warning` findings in Phase 3 and do not fail the command.
- **D-11:** File size warnings apply only to `.llm-wiki/raw/`, not to all wiki pages.
- **D-12:** A `.llm-wiki/raw/` file larger than 100 KB should produce a `warning`. This is meant to catch full logs, dumps, long generated output, and uncurated raw material.

### Staleness and Repo Path Drift
- **D-13:** Stale checks use only page frontmatter `updated:`.
- **D-14:** Pages without `updated:` are not stale-checked in Phase 3.
- **D-15:** A page with `updated:` older than 90 days should produce a `warning`.
- **D-16:** Stale findings only tell the user or agent to review the page against current repo files. Lint must not update `updated:` automatically.
- **D-17:** Phase 3 contradiction warnings are limited to conservative repo path drift. If a wiki page explicitly references a repo path that no longer exists, lint reports a warning.
- **D-18:** Repo path drift checks inspect only Markdown code spans and fenced code blocks for strings that look like repo paths. Lint should not scan ordinary prose for path-like text.
- **D-19:** Missing repo path references are `warning` findings, not errors, because they may be examples, future paths, or external paths.

### CLI Report Shape
- **D-20:** `project-wiki lint` exits `1` only when at least one `error` exists. Warning-only results exit `0`.
- **D-21:** Default output is human-readable text.
- **D-22:** Lint should also support optional `--json` output for CI and agent parsing.
- **D-23:** Severity names are exactly `error` and `warning` in Phase 3.
- **D-24:** Every finding uses fixed fields: `severity`, `code`, `path`, `message`, and `remediation`. JSON output uses the same fields.
- **D-25:** If no issues are found, lint should print an explicit success message such as `No issues found in .llm-wiki/`.
- **D-26:** Phase 3 lint does not modify files. It only reports findings and remediation guidance.

### the agent's Discretion
The planner may decide exact parser functions, finding codes, high-confidence secret patterns, path-detection heuristics, human-readable formatting, fixture layout, and test names. Keep the implementation standard-library only unless a later phase explicitly changes that constraint.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project and Requirements
- `.planning/PROJECT.md` — Defines the repo-local wiki concept, durable/volatile boundary, and Phase 3 current state.
- `.planning/REQUIREMENTS.md` — Defines Phase 3 requirements `LINT-01` through `LINT-07`, plus validation requirements `TEST-04` and `TEST-05`.
- `.planning/ROADMAP.md` — Defines Phase 3 goal, success criteria, and planned work slices.
- `.planning/STATE.md` — Records Phase 3 as the next phase and carries recent project decisions.
- `.planning/phases/02-init-and-wiki-templates/02-CONTEXT.md` — Locked Phase 2 decisions, especially raw source policy, Obsidian wikilinks, and the no-secret-scanning deferral to Phase 3.

### Package Surface
- `skills/project-llm-wiki/SKILL.md` — Skill triggers and lint mode boundary.
- `skills/project-llm-wiki/references/command-surface.md` — Documents planned `project-wiki-lint` behavior.
- `skills/project-llm-wiki/references/testing.md` — Current unittest command and validation style.

### Current Implementation and Fixtures
- `skills/project-llm-wiki/scripts/project_wiki.py` — Current CLI implementation; `lint` is still the Phase 3 planned-command stub.
- `skills/project-llm-wiki/tests/test_project_wiki_init.py` — Existing temporary Git repo fixture style and `.llm-wiki/` assertions.
- `skills/project-llm-wiki/tests/test_project_wiki_package.py` — Existing subprocess helper tests and stdlib import whitelist.
- `skills/project-llm-wiki/assets/templates/llm-wiki/index.md` — Current Obsidian wikilink style and default index shape.
- `skills/project-llm-wiki/assets/templates/llm-wiki/raw/README.md` — Raw source allow/deny policy.
- `skills/project-llm-wiki/assets/templates/llm-wiki/raw/curated/README.md` — Curated raw source requirements.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `skills/project-llm-wiki/scripts/project_wiki.py`: Existing argparse surface, Git-root resolver, path constants, and structured output helpers can be reused for lint.
- `skills/project-llm-wiki/tests/test_project_wiki_init.py`: Existing tests create temporary Git repos, run the helper as a subprocess, and inspect generated `.llm-wiki/` files. Phase 3 should continue this style for lint fixtures.
- `skills/project-llm-wiki/tests/test_project_wiki_package.py`: Import whitelist currently allows only `argparse`, `pathlib`, `subprocess`, `sys`, and `textwrap`; update only for additional stdlib modules actually used.

### Established Patterns
- Implementation is Python standard library only.
- Tests use `unittest` and subprocess-level assertions rather than a new test framework.
- The package keeps behavior inspectable across `SKILL.md`, references, scripts, templates, and tests.
- Init resolves the current Git root; lint should follow the same repository boundary and inspect `.llm-wiki/` inside the resolved Git root.

### Integration Points
- Replace the `lint` subcommand's planned handler in `project_wiki.py` with real lint behavior.
- Add lint-focused tests under `skills/project-llm-wiki/tests/`, either in a new lint test file or alongside existing helper tests if the planner keeps the suite small.
- Use current template files to create fixture wikis, then mutate them in tests to produce broken wikilinks, missing index entries, secret-looking content, large raw files, stale pages, and missing repo path references.

</code_context>

<specifics>
## Specific Ideas

- The user plans to open `.llm-wiki/` with Obsidian, so Phase 3 should prioritize Obsidian `[[wikilink]]` behavior.
- Lint findings should teach the user how to fix issues without pretending validation happened automatically.
- Stale page remediation should say to review the page against current repo files, then update `updated:` only after validation.
- File size warnings exist to prevent `.llm-wiki/raw/` from becoming a git-tracked dump/log bucket.

</specifics>

<deferred>
## Deferred Ideas

- `project-wiki lint --fix` or another auto-fix mode may be useful later, but Phase 3 should not auto-modify wiki files.
- General Markdown link linting may be added later if Obsidian wikilink linting proves insufficient.
- Heading-existence validation for `[[page#Heading]]` may be added later.
- Semantic repo/wiki contradiction detection is deferred; Phase 3 only performs deterministic repo path drift warnings.

</deferred>

---

*Phase: 3-Lint and Safety Checks*
*Context gathered: 2026-05-13*
