# Stack Research

**Domain:** Repo-local LLM wiki skills for coding agents
**Researched:** 2026-05-12
**Confidence:** MEDIUM

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

No external dependency should be required for v1.

```bash
# Expected shape, not final command contract
project-wiki-init
project-wiki-lint
project-wiki-query "What do we know about this repo?"
```

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

**If building as a vault-managed skill first:**
- Keep source under the vault `skills/project-llm-wiki/` pattern or mirror it from this repo.
- Use `SKILL.md`, `assets/`, `scripts/`, and `references/` as needed.

**If building as a standalone repo first:**
- Keep the reusable implementation in this repo, then install or symlink into `~/.codex/skills` or the vault-managed skills directory.
- Preserve tests in the repo so behavior can be validated independent of a specific target project.

**If target repo already has NotebookLM instructions:**
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

---
*Stack research for: repo-local LLM wiki skills*
*Researched: 2026-05-12*
