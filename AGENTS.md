<!-- GSD:project-start source:PROJECT.md -->
## Project

**Project LLM Wiki**

Project LLM Wiki is a reusable skill set for creating and maintaining a git-tracked `.llm-wiki/` knowledge layer inside each actual project repository. It adapts the Karpathy LLM Wiki pattern from a personal Obsidian vault into a per-repo operating surface for durable architecture notes, decisions, domain concepts, runbooks, feature summaries, and validated implementation learnings.

The skill should work in multi-repo workspaces by detecting the real git root and initializing `.llm-wiki/` inside the selected repository, not inside a parent folder that only groups projects. The initial rollout target is a single repo such as `peasydeal_be`, then the pattern can be applied to `peasydeal_web`, `peasydeal-product-miner`, and other repos after validation.

**Core Value:** Future agents and contributors can recover durable project context from the repository itself without confusing curated project knowledge with volatile task state.

### Constraints

- **Repository boundary**: Initialize inside the actual git root, not a multi-repo parent directory - prevents knowledge from landing in the wrong project.
- **Source of truth**: Trust the current repository over `.llm-wiki/` if they disagree - prevents stale notes from overriding code.
- **Durability boundary**: Store only curated, validated, non-secret knowledge in `.llm-wiki/` - keeps the wiki safe to commit.
- **State boundary**: Keep volatile workflow state in `.planning/`, Linear, OMX, or workflow files - prevents the wiki from becoming noisy and stale.
- **Idempotency**: Re-running init must not duplicate sections or overwrite existing notes - makes the skill safe for repeated use.
- **Merge safety**: Patch `AGENTS.md` with bounded markers or clearly scoped insertion rules - avoids damaging existing instructions such as NotebookLM sections.
- **Simplicity**: Prefer Markdown templates plus small scripts over new dependencies unless a dependency becomes clearly necessary.
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

## Recommended Stack
### Core Technologies
| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Markdown skill definitions | Current Codex and Claude skill formats | Defines triggers, protocol, safety rules, and usage examples | Existing vault skills are Markdown-first and easy to inspect, review, install, and version |
| Git-tracked `.llm-wiki/` directory | Git native | Stores durable repo-local project knowledge | Keeps context beside code and makes knowledge changes reviewable in diffs |
| Python 3 standard library | System Python 3 | Implements deterministic init, lint, wikilink parsing, secret scanning, and file updates | Strong enough for filesystem and text processing without adding runtime dependencies |
| Shell entry wrappers | POSIX-compatible shell | Lets skills call scripts with stable command surfaces | Matches existing local automation style and keeps commands easy to audit |
### Supporting Libraries
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pathlib` | Python stdlib | Path handling | Always use for repository and wiki paths |
| `subprocess` | Python stdlib | Git root detection via `git rev-parse` | Use for git operations rather than manually walking parent dirs when possible |
| `re` | Python stdlib | Wikilink, secret-looking pattern, and marker detection | Use for lint and merge-safe AGENTS patching |
| `argparse` | Python stdlib | CLI command parsing | Use if scripts expose init, lint, query helper modes |
| `unittest` or simple fixture scripts | Python stdlib | Regression tests | Use for idempotency, lint warnings, and AGENTS patch behavior |
### Development Tools
| Tool | Purpose | Notes |
|------|---------|-------|
| Git | Source control and git-root detection | `.llm-wiki/` should be visible in `git status` by default |
| `rg` | Fast local search | Useful for tests, inspection, and seed source discovery |
| GSD | Planning, phase execution, verification | `.planning/` remains workflow state, not project wiki content |
| Existing vault-managed skill patterns | Packaging reference | Follow `skills/<name>/SKILL.md`, optional `scripts/`, optional `assets/` |
## Installation
# Expected shape, not final command contract
## Alternatives Considered
| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Python stdlib scripts | Node.js CLI package | Use Node only if distribution through npm becomes a hard requirement |
| Markdown templates plus deterministic scripts | LLM-only skill instructions | LLM-only is acceptable for query synthesis, but init and lint need deterministic checks |
| `.llm-wiki/` in each git repo | One parent workspace wiki | Parent wiki is useful for cross-repo synthesis but fails the per-repo source-of-truth goal |
| Git-tracked wiki files | NotebookLM-only context | NotebookLM can answer questions, but it does not make durable repo-local knowledge reviewable |
## What NOT to Use
| Avoid | Why | Use Instead |
|-------|-----|-------------|
| New database or vector store in v1 | Adds operational weight before the Markdown contract is validated | Plain Markdown plus deterministic lint |
| Automatically storing full logs or dumps | High secret and noise risk | Curated summaries and redacted raw snippets |
| Broad AGENTS rewrites | High risk of clobbering existing repo instructions | Marker-bounded or section-aware patching |
| Hidden global-only state | Future contributors and agents will not see it from the repo | Git-tracked `.llm-wiki/` files |
## Stack Patterns by Variant
- Keep source under the vault `skills/project-llm-wiki/` pattern or mirror it from this repo.
- Use `SKILL.md`, `assets/`, `scripts/`, and `references/` as needed.
- Keep the reusable implementation in this repo, then install or symlink into `~/.codex/skills` or the vault-managed skills directory.
- Preserve tests in the repo so behavior can be validated independent of a specific target project.
- Patch only the Project LLM Wiki section.
- Do not overwrite the NotebookLM section.
## Version Compatibility
| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| Python 3 stdlib scripts | macOS development environment | Avoid non-stdlib packages for v1 |
| Codex skill format | `SKILL.md` plus optional folders | Keep trigger/protocol self-contained |
| Git repositories | `.llm-wiki/` root at `git rev-parse --show-toplevel` | Parent multi-repo workspaces must not receive the wiki by accident |
## Sources
- `projects/vault-llm-wiki/overview` - Karpathy LLM Wiki adaptation and layer split
- `projects/vault-llm-wiki/usage` - ingest, query, lint operations
- `skills/vault-ingest/SKILL` - compounding update protocol
- `skills/vault-query/SKILL` - query protocol with wikilink citations and log append
- `skills/vault-lint/SKILL` - structural and semantic lint categories
- `skills/README` - local skill packaging pattern
- `knowledge-graph/graphify` - structure-first navigation and machine memory separation
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- PROJECT-LLM-WIKI:CODEX-SUBAGENTS:START -->
## Codex Native Subagent Authorization

For GSD workflows in this repository, the user explicitly authorizes Codex native subagents for workflow `Task(...)` steps when they improve throughput, preserve intended role separation, or match the workflow's documented orchestration model.

When a GSD workflow calls `Task(subagent_type="gsd-*", prompt=...)`, map it to `spawn_agent(agent_type="gsd-*", message=...)` when the matching Codex agent is available. The lead agent still owns integration, verification, and final reporting.

If Codex runtime policy rejects automatic spawning in a given turn, fall back to inline execution and state that this was a runtime limitation, not a missing project authorization.
<!-- PROJECT-LLM-WIKI:CODEX-SUBAGENTS:END -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
