# Phase 03: lint-and-safety-checks - Research

**Researched:** 2026-05-13  
**Domain:** Deterministic Python-stdlib linting for repo-local `.llm-wiki/` Markdown  
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

All locked decisions, discretion areas, and deferred ideas in this section are copied from `.planning/phases/03-lint-and-safety-checks/03-CONTEXT.md`. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:13-119]

### Locked Decisions

#### Wikilink and Index Rules
- **D-01:** Lint should check only Obsidian-style `[[wikilink]]` links in Phase 3, not general Markdown links.
- **D-02:** Lint should support common Obsidian forms for page existence checks: `[[path]]`, `[[path.md]]`, `[[path|Alias]]`, and `[[path#Heading]]`.
- **D-03:** Alias text and heading fragments are ignored in Phase 3. Lint verifies that the linked page exists, but it does not validate that a heading exists.
- **D-04:** Broken wikilinks are `error` findings because they break Obsidian navigation.
- **D-05:** Main wiki pages should be discoverable from `.llm-wiki/index.md`. Missing index coverage for main wiki pages is a `warning`.
- **D-06:** `raw/curated/` source files are not required to be listed in `index.md`.
- **D-07:** A brand-new standalone topic page is not required to contain outgoing links. Lint should not force every page to link elsewhere.

#### Safety and Size Heuristics
- **D-08:** Secret-looking content detection should use high-confidence patterns only, to avoid noisy false positives in documentation.
- **D-09:** Secret-looking detection scans the entire `.llm-wiki/`, because secrets should not appear in any wiki page.
- **D-10:** Secret-looking findings are `warning` findings in Phase 3 and do not fail the command.
- **D-11:** File size warnings apply only to `.llm-wiki/raw/`, not to all wiki pages.
- **D-12:** A `.llm-wiki/raw/` file larger than 100 KB should produce a `warning`. This is meant to catch full logs, dumps, long generated output, and uncurated raw material.

#### Staleness and Repo Path Drift
- **D-13:** Stale checks use only page frontmatter `updated:`.
- **D-14:** Pages without `updated:` are not stale-checked in Phase 3.
- **D-15:** A page with `updated:` older than 90 days should produce a `warning`.
- **D-16:** Stale findings only tell the user or agent to review the page against current repo files. Lint must not update `updated:` automatically.
- **D-17:** Phase 3 contradiction warnings are limited to conservative repo path drift. If a wiki page explicitly references a repo path that no longer exists, lint reports a warning.
- **D-18:** Repo path drift checks inspect only Markdown code spans and fenced code blocks for strings that look like repo paths. Lint should not scan ordinary prose for path-like text.
- **D-19:** Missing repo path references are `warning` findings, not errors, because they may be examples, future paths, or external paths.

#### CLI Report Shape
- **D-20:** `project-wiki lint` exits `1` only when at least one `error` exists. Warning-only results exit `0`.
- **D-21:** Default output is human-readable text.
- **D-22:** Lint should also support optional `--json` output for CI and agent parsing.
- **D-23:** Severity names are exactly `error` and `warning` in Phase 3.
- **D-24:** Every finding uses fixed fields: `severity`, `code`, `path`, `message`, and `remediation`. JSON output uses the same fields.
- **D-25:** If no issues are found, lint should print an explicit success message such as `No issues found in .llm-wiki/`.
- **D-26:** Phase 3 lint does not modify files. It only reports findings and remediation guidance.

### the agent's Discretion
The planner may decide exact parser functions, finding codes, high-confidence secret patterns, path-detection heuristics, human-readable formatting, fixture layout, and test names. Keep the implementation standard-library only unless a later phase explicitly changes that constraint.

### Deferred Ideas (OUT OF SCOPE)
- `project-wiki lint --fix` or another auto-fix mode may be useful later, but Phase 3 should not auto-modify wiki files.
- General Markdown link linting may be added later if Obsidian wikilink linting proves insufficient.
- Heading-existence validation for `[[page#Heading]]` may be added later.
- Semantic repo/wiki contradiction detection is deferred; Phase 3 only performs deterministic repo path drift warnings.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| LINT-01 | User can run a structural lint that detects broken wikilinks. [VERIFIED: .planning/REQUIREMENTS.md:48] | Use an Obsidian wikilink extractor plus normalized wiki-root page lookup; broken links produce `error` findings. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:17-20] |
| LINT-02 | User can run a structural lint that detects files missing from `.llm-wiki/index.md`. [VERIFIED: .planning/REQUIREMENTS.md:49] | Build the main-page inventory from category Markdown pages and compare it to normalized index wikilinks. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:21-23] |
| LINT-03 | User can run a safety lint that detects secret-looking content in `.llm-wiki/raw/` and other wiki files. [VERIFIED: .planning/REQUIREMENTS.md:50] | Scan every `.llm-wiki/` file with high-confidence stdlib regex patterns and emit warning findings only. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:25-28] |
| LINT-04 | User can run a size lint that detects oversized raw files or generated dump-like files. [VERIFIED: .planning/REQUIREMENTS.md:51] | Check file byte size only under `.llm-wiki/raw/`; files over 100 KB produce warnings. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:29-30] |
| LINT-05 | User can run a freshness lint that flags stale wiki pages needing review. [VERIFIED: .planning/REQUIREMENTS.md:52] | Parse only top-of-file frontmatter `updated:` dates and warn when older than 90 days. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:32-36] |
| LINT-06 | User can receive likely repo/wiki contradiction warnings when wiki claims appear to disagree with current repo files. [VERIFIED: .planning/REQUIREMENTS.md:53] | Implement conservative repo path drift warnings from code spans and fenced code blocks only. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:37-39] |
| LINT-07 | Lint output includes file paths, issue type, severity, and actionable remediation guidance. [VERIFIED: .planning/REQUIREMENTS.md:54] | Use fixed finding fields `severity`, `code`, `path`, `message`, and `remediation` in text and JSON output. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:41-48] |
| TEST-04 | Lint with an intentionally missing index entry reports the issue. [VERIFIED: .planning/REQUIREMENTS.md:69] | Add a temp Git repo fixture that runs init, removes an index wikilink, runs lint, and asserts a `missing_index_entry` warning. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_init.py:23-41,267-290] |
| TEST-05 | Lint with an intentionally secret-looking raw file reports the issue. [VERIFIED: .planning/REQUIREMENTS.md:70] | Add a temp Git repo fixture that writes a high-confidence secret-looking raw file and asserts a `secret_like_content` warning. [VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/raw/README.md:11-20] |
</phase_requirements>

## Summary

Phase 3 should replace the current `lint` planned-command stub in `skills/project-llm-wiki/scripts/project_wiki.py` with a deterministic, read-only lint pipeline that reuses the existing Git-root resolver, `.llm-wiki` constants, concise output helpers, and subprocess-tested CLI surface. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:57-73,250-270,367-368] The implementation should stay in Python standard library modules, because both project constraints and the package import whitelist enforce a no-new-dependency contract. [VERIFIED: AGENTS.md:20,32-41; skills/project-llm-wiki/tests/test_project_wiki_package.py:67-81]

The safest implementation shape is: resolve the current Git root, locate `.llm-wiki/`, collect candidate files in deterministic sorted order, build a normalized wikilink/page index, run each locked check in a stable order, render findings with fixed fields, and return `1` only when an `error` finding exists. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:41-48] The default skeleton should lint cleanly, so index coverage should not require `.llm-wiki/README.md`, `.llm-wiki/AGENTS.md`, or `.llm-wiki/log.md` to be linked from `index.md`; main content pages should be the category Markdown pages plus raw policy README pages, while `raw/curated/` source files remain excluded. [VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/index.md:1-34; .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:21-23]

**Primary recommendation:** implement one `run_lint(args)` function with small pure helpers for file discovery, wikilink normalization, index coverage, secret regex matching, raw-size warnings, frontmatter date parsing, repo-path extraction, finding rendering, and exit-code calculation. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:273-332,335-376]

## Project Constraints (from AGENTS.md)

- The wiki must live inside the actual git root, not a multi-repo parent directory. [VERIFIED: AGENTS.md:14; skills/project-llm-wiki/scripts/project_wiki.py:62-73]
- Current repository files are authoritative when they disagree with `.llm-wiki/`. [VERIFIED: AGENTS.md:15; skills/project-llm-wiki/SKILL.md:21-25]
- `.llm-wiki/` is for curated, validated, non-secret durable knowledge; volatile workflow state stays in `.planning/`, Linear, OMX, or workflow files. [VERIFIED: AGENTS.md:16-17]
- Prefer Markdown templates plus small scripts over new dependencies unless a dependency becomes clearly necessary. [VERIFIED: AGENTS.md:20]
- The current stack lists Python stdlib modules for deterministic init, lint, wikilink parsing, secret scanning, and tests. [VERIFIED: AGENTS.md:30-41]
- The package quality check is `python3 -m unittest discover -s skills/project-llm-wiki/tests`. [VERIFIED: skills/project-llm-wiki/SKILL.md:47-49; skills/project-llm-wiki/references/testing.md:3-8]
- The import whitelist test currently allows only `argparse`, `pathlib`, `subprocess`, `sys`, and `textwrap`; Phase 3 must update it only for stdlib imports actually used by lint, likely `datetime`, `json`, and `re`. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py:67-81]
- No project-local skill directories were present at `.codex/skills/` or `.agents/skills/` during research. [VERIFIED: `find .codex/skills .agents/skills -maxdepth 3 -type f -name SKILL.md` exited with both directories missing]
- No `.planning/graphs/graph.json` was present, so no graph context was available for this phase. [VERIFIED: `ls .planning/graphs/graph.json` returned no such file]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| CLI command parsing and `--json` flag | Local CLI script | Python stdlib `argparse` | `project_wiki.py` already owns subcommands through `argparse`; adding `lint --json` there preserves the existing command surface. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:335-376; CITED: https://docs.python.org/3/library/argparse.html] |
| Git-root and wiki-root resolution | Local CLI script | Git executable and filesystem | Init already resolves `git rev-parse --show-toplevel`; lint should use the same repository boundary. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:62-73,273-286] |
| Wikilink and index checks | Local CLI script | `.llm-wiki/` Markdown files | The locked scope is deterministic Obsidian wikilinks and index coverage, not LLM synthesis. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:16-23; CITED: https://obsidian.md/help/links] |
| Secret-looking and raw-size checks | Local CLI script | `.llm-wiki/` filesystem bytes/text | Phase 3 reports safety warnings without modifying files or adding a third-party scanner. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:25-30,48] |
| Stale page and repo path drift checks | Local CLI script | `.llm-wiki/` Markdown plus current repo filesystem | Staleness is based on frontmatter `updated:`; contradiction checks are limited to missing repo path references in code spans/blocks. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:32-39] |
| Exit codes and output shape | Local CLI script | CI/agent callers | Exit `1` is reserved for `error` findings; warnings remain visible but non-blocking. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:41-48] |
| Regression validation | Python unittest suite | Temporary Git repositories | Existing tests already run helper subprocesses against temp Git repos, which is the right boundary for lint fixtures. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_init.py:13-50; CITED: https://docs.python.org/3/library/unittest.html] |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.14.3 local runtime | Execute the helper script and stdlib tests | The local validation runtime is Python 3.14.3, and the project already uses Python stdlib for CLI behavior. [VERIFIED: `python3 --version`; VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:1-6] |
| `argparse` | Python 3.14 stdlib | Add `lint --json` and keep CLI help/error behavior | Existing helper uses `argparse`; official docs describe subcommands, flags, generated help, and invalid-argument handling. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:335-376; CITED: https://docs.python.org/3/library/argparse.html] |
| `pathlib` | Python 3.14 stdlib | Traverse `.llm-wiki/`, normalize relative paths, check existence and sizes | Existing code uses `pathlib.Path` for all repo/wiki paths; official docs cover recursive glob/walk and path existence helpers. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:10-54,93-110,155-160; CITED: https://docs.python.org/3/library/pathlib.html] |
| `subprocess` | Python 3.14 stdlib | Preserve `git rev-parse --show-toplevel` root detection | Existing `resolve_git_root` already shells to Git with an argument list and `check=False`. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:62-73] |
| `re` | Python 3.14 stdlib | Implement targeted wikilink, secret-looking, frontmatter, and code-span/path regexes | The project stack already lists `re` for wikilink and secret-looking checks; official docs support compiled/module regex operations and warn to use raw strings for backslash-heavy patterns. [VERIFIED: AGENTS.md:37-41; CITED: https://docs.python.org/3/library/re.html] |
| `json` | Python 3.14 stdlib | Render stable `--json` output for CI and agents | Python stdlib provides `json.dumps`, indentation, and sorted-key serialization for deterministic output. [CITED: https://docs.python.org/3/library/json.html] |
| `datetime` | Python 3.14 stdlib | Parse frontmatter `updated:` dates and compare against a 90-day threshold | `datetime.date.fromisoformat` parses ISO date strings; Phase 3 stale checks use frontmatter `updated:` only. [CITED: https://docs.python.org/3/library/datetime.html; VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:32-36] |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `unittest` | Python 3.14 stdlib | Run subprocess-level lint fixtures | Continue the existing test framework and discovery command. [VERIFIED: skills/project-llm-wiki/references/testing.md:3-8; CITED: https://docs.python.org/3/library/unittest.html] |
| `tempfile` | Python 3.14 stdlib | Create isolated temporary Git repos for lint fixtures | Existing init tests use `tempfile.TemporaryDirectory()` for clean repo fixtures. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_init.py:52-347] |
| `sys` | Python 3.14 stdlib | Run the helper with the active Python executable in tests | Existing tests use `sys.executable` to invoke `project_wiki.py`. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_init.py:34-41] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Targeted stdlib regexes | Full Markdown parser | Not needed because the locked scope is Obsidian wikilinks, top frontmatter, code spans, and fenced code blocks only. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:16-23,32-39] |
| High-confidence stdlib secret heuristics | External secret scanner | External scanners improve coverage but violate the Phase 3 no-new-dependency constraint unless a later phase changes it. [VERIFIED: AGENTS.md:20,37-41; VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:50-51] |
| Deterministic repo path drift | Semantic contradiction detection | Semantic detection is explicitly deferred; Phase 3 only warns on missing repo paths found in code spans/blocks. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:113-119] |

**Installation:**

No package installation is required for Phase 3. [VERIFIED: AGENTS.md:20,32-41]

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests
```

**Version verification:** No npm packages are recommended. The local runtime probes during research returned `Python 3.14.3` and `git version 2.50.1 (Apple Git-155)`. [VERIFIED: `python3 --version`; VERIFIED: `git --version`]

## Architecture Patterns

### System Architecture Diagram

```text
User / Agent
  |
  v
project-wiki lint [--json]
  |
  v
resolve_git_root(cwd)
  |
  +-- no Git repo -> operational exit 2
  |
  v
load .llm-wiki/ inventory
  |
  +-- missing/unreadable required wiki root -> operational exit 2 or lint finding
  |
  v
build normalized page and index-link maps
  |
  +--> broken wikilink check -> error findings
  +--> missing index coverage check -> warning findings
  +--> raw file size check -> warning findings
  +--> high-confidence secret-looking check -> warning findings
  +--> updated: staleness check -> warning findings
  +--> code span/block repo path drift check -> warning findings
  |
  v
sort findings deterministically
  |
  +--> text output -> human remediation guidance
  +--> JSON output -> {"findings": [{severity, code, path, message, remediation}]}
  |
  v
exit 1 if any error else 0
```

This flow matches the existing helper's local CLI responsibility and the locked exit-code contract. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:335-383; VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:41-48]

### Recommended Project Structure

```text
skills/project-llm-wiki/
├── scripts/
│   └── project_wiki.py           # Replace lint stub with run_lint and helpers
├── tests/
│   ├── test_project_wiki_init.py
│   ├── test_project_wiki_package.py
│   └── test_project_wiki_lint.py # New Phase 3 lint subprocess fixtures
├── assets/templates/llm-wiki/
│   ├── index.md
│   └── raw/
└── references/
    ├── command-surface.md
    └── testing.md
```

This structure follows the existing package layout and test discovery command. [VERIFIED: `find skills/project-llm-wiki -maxdepth 4 -type f`; VERIFIED: skills/project-llm-wiki/references/testing.md:3-8]

### Pattern 1: Finding Records as the Internal Contract

**What:** Represent every lint issue as a dictionary with exactly `severity`, `code`, `path`, `message`, and `remediation`. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:41-48]  
**When to use:** Use this for all lint checks before any text or JSON rendering. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:43-46]  
**Example:**

```python
# Source: Phase 3 context fixed fields; Python json docs for serialization.
finding = {
    "severity": "warning",
    "code": "missing_index_entry",
    "path": ".llm-wiki/features/ideas.md",
    "message": "Main wiki page is not linked from .llm-wiki/index.md.",
    "remediation": "Add [[features/ideas]] to .llm-wiki/index.md.",
}
```

### Pattern 2: Obsidian Wikilink Normalization

**What:** Extract `[[...]]`, split display aliases at `|`, split heading fragments at `#`, preserve explicit file extensions, and otherwise resolve Markdown page targets as wiki-root-relative `.md` paths. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:17-20; CITED: https://obsidian.md/help/links]  
**When to use:** Use this for both broken-link checks and index coverage checks so `[[path]]`, `[[path.md]]`, `[[path|Alias]]`, and `[[path#Heading]]` behave consistently. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:17-20]  
**Edge rule:** If a target has a non-`.md` suffix, check that exact file under `.llm-wiki/` rather than appending `.md`; Obsidian documents non-Markdown links as extension-bearing links. [CITED: https://obsidian.md/help/links]

### Pattern 3: Main Page Index Coverage

**What:** Treat category Markdown pages under `architecture/`, `domain/`, `decisions/`, `operations/`, `features/`, and `summaries/` as main wiki pages; also treat `raw/README.md` and `raw/curated/README.md` as policy pages; exclude `.llm-wiki/index.md`, `.llm-wiki/README.md`, `.llm-wiki/AGENTS.md`, `.llm-wiki/log.md`, `.gitkeep`, and `raw/curated/` source files. [VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/index.md:1-34; VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:21-23]  
**When to use:** Use this for LINT-02 and TEST-04 so the default Phase 2 skeleton is not noisy, while real content pages remain discoverable. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_init.py:245-265,267-290]

### Pattern 4: Conservative Safety Heuristics

**What:** Use high-confidence patterns such as private key PEM headers and credential-bearing database URLs; keep generic keyword-only checks out of Phase 3. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:25-28; CITED: https://docs.github.com/en/code-security/secret-scanning/introduction/supported-secret-scanning-patterns]  
**When to use:** Use this for LINT-03 and TEST-05; the warning should tell the user to remove/redact the material and rotate credentials if the value was real. [VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/raw/README.md:11-20]

### Pattern 5: Code-Span-Only Repo Path Drift

**What:** Track fenced code blocks by fence lines and scan inline code spans outside fences; do not scan ordinary prose. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:37-39]  
**When to use:** Use this for LINT-06; only warn on candidates that look repo-local, such as `skills/project-llm-wiki/scripts/project_wiki.py`, `./README.md`, or `.planning/ROADMAP.md`, and ignore URLs, absolute home/temp paths, anchors, and values with spaces. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:37-39]

### Anti-Patterns to Avoid

- **Broad Markdown link linting:** Phase 3 explicitly excludes general Markdown links, so only parse `[[wikilink]]` tokens. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:16-20]
- **Secret keyword scanning:** Warning on words like "token" or "credential" alone would conflict with the high-confidence-only decision and the raw policy documentation itself. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:25-28; VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/raw/README.md:11-20]
- **Warning-only nonzero exit:** Warnings must remain exit `0`, so only broken wikilink errors should fail normal lint in Phase 3 unless an operational failure occurs. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:41-42]
- **Auto-fixing index or dates:** Phase 3 lint is read-only and must not update `index.md` or frontmatter. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:36,48,116]
- **Unsorted filesystem output:** `Path.rglob()` results are documented as unordered, so sort paths and findings before rendering to keep tests stable. [CITED: https://docs.python.org/3/library/pathlib.html]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Full Markdown parsing | A custom Markdown AST parser | Targeted stdlib regex/state helpers for locked constructs | Phase 3 checks only wikilinks, top frontmatter, inline code spans, and fenced code blocks. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:16-39] |
| Secret scanning platform | Provider verification, entropy scoring, or external scanners | High-confidence regex warnings for private keys and credential URLs | The phase must stay no-dependency and warning-only for secret-looking content. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:25-30,50-51] |
| YAML parser | Full YAML frontmatter support | Minimal top-block scan for `updated: YYYY-MM-DD` | Stale checks use only the `updated:` field; Python `date.fromisoformat` handles ISO dates. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:32-36; CITED: https://docs.python.org/3/library/datetime.html] |
| Semantic contradiction engine | AI comparison of wiki claims to code | Missing repo path warnings from code spans/blocks | Semantic contradiction detection is deferred. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:113-119] |
| Separate test framework | Pytest or snapshot plugins | `unittest`, `tempfile`, `subprocess`, and JSON parsing | Existing validation uses stdlib unittest and subprocess helpers. [VERIFIED: skills/project-llm-wiki/references/testing.md:3-41] |

**Key insight:** Phase 3 should be deterministic guardrail code, not a broad content intelligence system. [VERIFIED: .planning/research/PITFALLS.md:107-117; VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:113-119]

## Common Pitfalls

### Pitfall 1: Default Skeleton Produces Index Warnings

**What goes wrong:** Lint treats `.llm-wiki/README.md`, `.llm-wiki/AGENTS.md`, or `.llm-wiki/log.md` as missing index entries even though the default index does not link them. [VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/index.md:1-34]  
**Why it happens:** "All Markdown files" is simpler than "main wiki pages." [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:21-23]  
**How to avoid:** Define main-page coverage as category content pages plus raw policy README pages, excluding root operational files and `raw/curated/` source files. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:21-23]  
**Warning signs:** A clean Phase 2 init produces warnings before any user content is added. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_init.py:245-265]

### Pitfall 2: Wikilink Parsing Treats Alias or Heading as File Path

**What goes wrong:** `[[features/ideas|Ideas]]` or `[[features/ideas#Later]]` incorrectly looks for a file with `|Ideas` or `#Later` in the name. [CITED: https://obsidian.md/help/links]  
**Why it happens:** The parser validates the raw link body instead of normalizing the destination. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:17-20]  
**How to avoid:** Strip alias and heading fragments before page existence checks. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:18-20]  
**Warning signs:** Tests for alias and heading links fail even when the destination page exists. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:18-20]

### Pitfall 3: Secret Scanner Becomes Noisy

**What goes wrong:** Raw policy pages themselves trigger warnings because they mention secrets, credentials, tokens, and dumps. [VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/raw/README.md:11-20]  
**Why it happens:** The implementation matches sensitive words rather than high-confidence secret shapes. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:25-28]  
**How to avoid:** Match private key blocks and credential-bearing URLs; avoid keyword-only patterns. [CITED: https://docs.github.com/en/code-security/secret-scanning/introduction/supported-secret-scanning-patterns]  
**Warning signs:** A clean skeleton warns on `raw/README.md`. [VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/raw/README.md:11-20]

### Pitfall 4: Date Tests Become Time-Sensitive

**What goes wrong:** A stale-date test passes or fails depending on the day it runs. [CITED: https://docs.python.org/3/library/datetime.html]  
**Why it happens:** The fixture picks a date near the 90-day threshold. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:32-36]  
**How to avoid:** Use a clearly old date such as `2000-01-01` for stale warnings and `datetime.date.today().isoformat()` for non-stale controls. [CITED: https://docs.python.org/3/library/datetime.html]  
**Warning signs:** Tests fail around threshold dates or across time zones. [ASSUMED]

### Pitfall 5: Repo Path Drift Scans Prose

**What goes wrong:** Lint warns on examples or ordinary prose that were never intended as validated repo paths. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:37-39]  
**Why it happens:** The implementation searches the whole Markdown body for path-like strings. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:37-39]  
**How to avoid:** Scan only inline code spans and fenced code blocks. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:37-39]  
**Warning signs:** Warnings appear for non-code prose sentences. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:37-39]

## Code Examples

Verified patterns from official and local sources:

### Stable JSON Rendering

```python
# Source: Python json docs and Phase 3 fixed finding fields.
payload = {"findings": findings}
print(json.dumps(payload, indent=2, sort_keys=True))
```

Use `sort_keys=True` and a fixed top-level `findings` key to make fixture assertions stable. [CITED: https://docs.python.org/3/library/json.html; VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:44-46]

### ISO Date Parsing for `updated:`

```python
# Source: Python datetime docs.
updated = datetime.date.fromisoformat(value)
is_stale = (datetime.date.today() - updated).days > 90
```

Use this only after extracting `updated:` from the top frontmatter block. [CITED: https://docs.python.org/3/library/datetime.html; VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:32-36]

### Existing Subprocess Fixture Style

```python
# Source: existing test helper style.
result = subprocess.run(
    [sys.executable, str(HELPER), "lint", "--json"],
    cwd=repo,
    capture_output=True,
    text=True,
    check=False,
)
```

Continue testing lint through the helper subprocess boundary, because existing tests validate CLI behavior that way. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_init.py:34-41]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| LLM-only wiki hygiene | Deterministic lint helpers for broken links, index gaps, stale dates, secret-like content, and raw size | Project research before v1 planning | Repeatable checks prevent the wiki from becoming unsafe or stale. [VERIFIED: .planning/research/PITFALLS.md:107-117] |
| Markdown links as generic wiki links | Obsidian `[[wikilink]]` support first | Phase 3 context on 2026-05-13 | Supports the intended Obsidian workflow while avoiding broader Markdown parsing. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:16-20; CITED: https://obsidian.md/help/links] |
| Secret policy only | Warning-only high-confidence secret-looking lint | Phase 3 context on 2026-05-13 | Makes unsafe material visible without pretending Phase 3 is a complete secret scanner. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:25-30] |

**Deprecated/outdated:**
- The current `project-wiki lint` stub is obsolete for Phase 3 planning because it still calls `planned_command("project-wiki-lint", "Phase 3")` and exits `2`. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:367-368; VERIFIED: `python3 skills/project-llm-wiki/scripts/project_wiki.py lint`]
- The current `lint --help` lacks `--json`; Phase 3 must add it to satisfy D-22. [VERIFIED: `python3 skills/project-llm-wiki/scripts/project_wiki.py lint --help`; VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:43-44]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Time-zone-sensitive stale tests may fail around thresholds. [ASSUMED] | Common Pitfalls | Low; choose dates far from the 90-day boundary or compute current dates in fixtures. |

## Open Questions (RESOLVED)

1. **RESOLVED: Should unreadable Markdown files be lint `error` findings or operational exit `2`?**
   - What we know: init treats an unreadable existing `index.md` as a conflict and exits `2`. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:192-201,320-323]
   - What's unclear: Phase 3 context does not explicitly classify unreadable wiki files. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:16-48]
   - RESOLVED: Missing Git repo or missing `.llm-wiki/` remains an operational exit `2`; unreadable wiki files inside an existing wiki produce lint `error` findings with path and remediation so text and JSON output can report them. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:46-48]

2. **RESOLVED: Should provider-specific token prefixes be included in Phase 3?**
   - What we know: GitHub documents many supported secret scanning patterns and high-precision generic private key/database URL patterns. [CITED: https://docs.github.com/en/code-security/secret-scanning/introduction/supported-secret-scanning-patterns]
   - What's unclear: Phase 3 context delegates exact high-confidence secret patterns to the planner. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:50-51]
   - RESOLVED: Phase 3 starts with generic high-confidence private key delimiters and credential-bearing URLs only; provider-specific token prefixes are deferred unless later tests add false-positive coverage. [VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/raw/README.md:11-20]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python 3 | Helper script and unittest suite | yes | 3.14.3 | None needed. [VERIFIED: `python3 --version`] |
| Git | Git-root detection and temp repo fixtures | yes | 2.50.1 Apple Git-155 | None needed for this project because git-root detection is a core requirement. [VERIFIED: `git --version`; VERIFIED: .planning/REQUIREMENTS.md:48-54] |
| Python stdlib `unittest` | Validation suite | yes | Python 3.14 stdlib | None needed. [CITED: https://docs.python.org/3/library/unittest.html] |
| `rg` | Research/search only | yes | command available during research | Fallback to shell/Python search if absent. [VERIFIED: `rg -n ...` completed during research] |

**Missing dependencies with no fallback:** None found. [VERIFIED: environment probes above]

**Missing dependencies with fallback:** None found for Phase 3 implementation. [VERIFIED: environment probes above]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python `unittest` through stdlib discovery. [VERIFIED: skills/project-llm-wiki/references/testing.md:3-8; CITED: https://docs.python.org/3/library/unittest.html] |
| Config file | None. Existing tests are discovered from `skills/project-llm-wiki/tests`. [VERIFIED: skills/project-llm-wiki/references/testing.md:3-8] |
| Quick run command | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests -p "test_project_wiki_lint.py"` [VERIFIED: Python unittest discovery supports `-s` and `-p`; CITED: https://docs.python.org/3/library/unittest.html] |
| Full suite command | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests` [VERIFIED: skills/project-llm-wiki/references/testing.md:3-8] |
| Current baseline | Full suite passed 22 tests during research. [VERIFIED: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests`] |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| LINT-01 | Broken wikilink reports `error`, includes path/code/remediation, and exits `1`. [VERIFIED: .planning/REQUIREMENTS.md:48; VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:17-20] | integration | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests -p "test_project_wiki_lint.py"` | No - Wave 0 gap. [VERIFIED: `find skills/project-llm-wiki/tests -maxdepth 1 -type f`] |
| LINT-02 | Missing main page index entry reports warning and exits `0`. [VERIFIED: .planning/REQUIREMENTS.md:49; VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:21-23] | integration | same lint test command | No - Wave 0 gap. [VERIFIED: `find skills/project-llm-wiki/tests -maxdepth 1 -type f`] |
| LINT-03 | High-confidence secret-looking content anywhere under `.llm-wiki/` reports warning and exits `0`. [VERIFIED: .planning/REQUIREMENTS.md:50; VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:25-28] | integration | same lint test command | No - Wave 0 gap. [VERIFIED: `find skills/project-llm-wiki/tests -maxdepth 1 -type f`] |
| LINT-04 | `.llm-wiki/raw/` file over 100 KB reports warning and exits `0`. [VERIFIED: .planning/REQUIREMENTS.md:51; VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:29-30] | integration | same lint test command | No - Wave 0 gap. [VERIFIED: `find skills/project-llm-wiki/tests -maxdepth 1 -type f`] |
| LINT-05 | Frontmatter `updated:` older than 90 days reports stale warning; missing `updated:` is ignored. [VERIFIED: .planning/REQUIREMENTS.md:52; VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:32-36] | integration | same lint test command | No - Wave 0 gap. [VERIFIED: `find skills/project-llm-wiki/tests -maxdepth 1 -type f`] |
| LINT-06 | Missing repo path in inline code span or fenced code block reports warning; ordinary prose is ignored. [VERIFIED: .planning/REQUIREMENTS.md:53; VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:37-39] | integration | same lint test command | No - Wave 0 gap. [VERIFIED: `find skills/project-llm-wiki/tests -maxdepth 1 -type f`] |
| LINT-07 | Text and JSON output include fixed fields and actionable remediation; JSON parses with stdlib `json`. [VERIFIED: .planning/REQUIREMENTS.md:54; VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:41-48] | integration | same lint test command plus full suite | No - Wave 0 gap. [VERIFIED: `python3 skills/project-llm-wiki/scripts/project_wiki.py lint --help`] |
| TEST-04 | Missing index entry fixture reports issue. [VERIFIED: .planning/REQUIREMENTS.md:69] | integration | same lint test command | No - Wave 0 gap. [VERIFIED: `find skills/project-llm-wiki/tests -maxdepth 1 -type f`] |
| TEST-05 | Secret-looking raw file fixture reports issue. [VERIFIED: .planning/REQUIREMENTS.md:70] | integration | same lint test command | No - Wave 0 gap. [VERIFIED: `find skills/project-llm-wiki/tests -maxdepth 1 -type f`] |

### Sampling Rate

- **Per task commit:** Run `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests -p "test_project_wiki_lint.py"` after lint edits. [VERIFIED: skills/project-llm-wiki/references/testing.md:3-8]
- **Per wave merge:** Run `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests` after each plan. [VERIFIED: skills/project-llm-wiki/references/testing.md:3-8]
- **Phase gate:** Full suite green, plus manual spot-checks for `lint`, `lint --json`, `lint --help`, no-issue output, warning-only exit `0`, and broken-link exit `1`. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:41-48]

### Wave 0 Gaps

- [ ] `skills/project-llm-wiki/tests/test_project_wiki_lint.py` - subprocess fixtures for LINT-01 through LINT-07, TEST-04, and TEST-05. [VERIFIED: no existing lint test file under skills/project-llm-wiki/tests]
- [ ] Update `skills/project-llm-wiki/tests/test_project_wiki_package.py` import whitelist for actual new stdlib imports, likely `datetime`, `json`, and `re`. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py:67-81]
- [ ] Add tests that default Phase 2 init lint has no findings and prints `No issues found in .llm-wiki/`. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:47]
- [ ] Add tests for JSON output shape and parseability. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:44-46]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | No authentication surface is introduced by local lint. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:6-10] |
| V3 Session Management | no | No sessions are introduced by local lint. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:6-10] |
| V4 Access Control | yes | Restrict lint traversal to the resolved Git root and `.llm-wiki/`; do not follow symlinked wiki roots outside the repo. [VERIFIED: AGENTS.md:14; VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:155-189; CITED: https://docs.python.org/3/library/pathlib.html] |
| V5 Input Validation | yes | Normalize wikilinks, frontmatter dates, and repo path candidates with deterministic parsers and reject/suppress ambiguous inputs. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:16-39] |
| V6 Cryptography | yes | Do not implement cryptography; only detect high-confidence private key material as warning findings. [CITED: https://docs.github.com/en/code-security/secret-scanning/introduction/supported-secret-scanning-patterns] |
| V8 Data Protection | yes | Secret-looking content scanning protects the git-tracked wiki from accidental unsafe material. [VERIFIED: AGENTS.md:16; VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:25-30] |
| V14 Configuration | yes | Output and exit codes must remain stable for CI/agent parsing. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:41-48] |

### Known Threat Patterns for Local Wiki Lint

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Symlink escape from `.llm-wiki/` to files outside the Git root | Information Disclosure | Reuse `path_is_under`, reject symlinked required wiki roots, and do not follow recursive symlinks. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:155-189; CITED: https://docs.python.org/3/library/pathlib.html] |
| Unsafe raw source committed to git | Information Disclosure | Warn on high-confidence private key/credential URL shapes and raw files over 100 KB. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:25-30; CITED: https://docs.github.com/en/code-security/secret-scanning/introduction/supported-secret-scanning-patterns] |
| Stale wiki overrides current repo code | Tampering | Warn on `updated:` dates older than 90 days and missing repo path references. [VERIFIED: AGENTS.md:15; VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:32-39] |
| CI misinterprets warnings as failures | Denial of Service | Return `1` only for `error` findings and `0` for warning-only runs. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:41-42] |

## Sources

### Primary (HIGH confidence)
- `.planning/phases/03-lint-and-safety-checks/03-CONTEXT.md` - locked Phase 3 decisions, boundaries, and deferred scope. [VERIFIED: local file]
- `.planning/REQUIREMENTS.md` - LINT-01 through LINT-07 and TEST-04 through TEST-05. [VERIFIED: local file]
- `AGENTS.md` - project constraints, stack, and workflow rules. [VERIFIED: local file]
- `skills/project-llm-wiki/scripts/project_wiki.py` - existing CLI, git-root resolver, init patterns, and lint stub. [VERIFIED: local file]
- `skills/project-llm-wiki/tests/test_project_wiki_init.py` and `test_project_wiki_package.py` - existing subprocess fixture style and import whitelist. [VERIFIED: local files]
- `skills/project-llm-wiki/assets/templates/llm-wiki/index.md` and `raw/README.md` - default index and raw safety policy. [VERIFIED: local files]
- Python docs: `argparse`, `pathlib`, `re`, `json`, `datetime`, and `unittest`. [CITED: https://docs.python.org/3/library/argparse.html, https://docs.python.org/3/library/pathlib.html, https://docs.python.org/3/library/re.html, https://docs.python.org/3/library/json.html, https://docs.python.org/3/library/datetime.html, https://docs.python.org/3/library/unittest.html]
- Obsidian Help internal links documentation. [CITED: https://obsidian.md/help/links]

### Secondary (MEDIUM confidence)
- GitHub Docs supported secret scanning patterns, used only to justify high-confidence generic private-key and credential URL categories, not to import a full scanner. [CITED: https://docs.github.com/en/code-security/secret-scanning/introduction/supported-secret-scanning-patterns]
- `.planning/research/STACK.md`, `.planning/research/PITFALLS.md`, and `.planning/research/ARCHITECTURE.md` - earlier project research supporting deterministic stdlib lint and no LLM-only safety checks. [VERIFIED: local files]

### Tertiary (LOW confidence)
- None used. [VERIFIED: source list above]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - local project constraints, existing code, and official Python docs agree on Python stdlib only. [VERIFIED: AGENTS.md:20,32-41; CITED: https://docs.python.org/3/library/]
- Architecture: HIGH - the current helper already owns Git-root resolution and CLI subcommands; Phase 3 only replaces the `lint` stub. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:62-73,335-376]
- Pitfalls: HIGH - the main risks are directly covered by locked decisions and existing default templates. [VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:16-48; VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/index.md:1-34]
- Secret patterns: MEDIUM - generic high-confidence categories are documented, but exact Phase 3 regexes remain planner discretion. [CITED: https://docs.github.com/en/code-security/secret-scanning/introduction/supported-secret-scanning-patterns; VERIFIED: .planning/phases/03-lint-and-safety-checks/03-CONTEXT.md:50-51]

**Research date:** 2026-05-13  
**Valid until:** 2026-06-12 for stdlib/local architecture; re-check secret-pattern docs if provider-specific patterns are added.
