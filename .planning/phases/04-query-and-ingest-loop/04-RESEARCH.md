# Phase 04: Query and Ingest Loop - Research

**Researched:** 2026-05-13  
**Domain:** Repo-local Markdown wiki query and curated ingest protocol  
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

All locked decisions, discretion areas, and deferred ideas in this section are copied from `.planning/phases/04-query-and-ingest-loop/04-CONTEXT.md`. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]

### Locked Decisions

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

### Deferred Ideas (OUT OF SCOPE)

- A future optional video-analysis adapter can standardize YouTube preprocessing, but Phase 4 core ingest should stay adapter-agnostic.
- A future dedicated raw-source verification mode may help decide which curated excerpts should be retained long-term.
- Embedding/vector search or qmd-style search can be added later if the index stops being enough.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| QUERY-01 | User can query project wiki knowledge and the skill reads `.llm-wiki/index.md` before reading individual wiki pages. [VERIFIED: .planning/REQUIREMENTS.md] | Make `index.md` the first read in the skill protocol and in helper discovery; use extracted index wikilinks as the candidate page set. [VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/index.md; VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:319-330] |
| QUERY-02 | User receives answers that cite repo-local wiki pages with `[[wikilink]]` citations. [VERIFIED: .planning/REQUIREMENTS.md] | Put the citation rule in `SKILL.md` and command docs; helper output should name pages in wikilink form but must not synthesize final answers. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md] |
| QUERY-03 | User receives a clear not-covered answer when `.llm-wiki/` has no relevant coverage, with a suggestion to ingest or initialize relevant pages. [VERIFIED: .planning/REQUIREMENTS.md] | Implement a not-covered response template that lists consulted pages and suggests source types, not a full ingest draft. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md] |
| QUERY-04 | User queries append an entry to `.llm-wiki/log.md` with date, query summary, pages consulted, and key insight. [VERIFIED: .planning/REQUIREMENTS.md] | Add a reusable log-append helper and require the agent protocol to call it after answering or not-covered handling. [VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/log.md] |
| INGEST-01 | User can ingest a curated project source into `.llm-wiki/` without storing unsafe raw material. [VERIFIED: .planning/REQUIREMENTS.md] | Validate source kind, keep raw persistence optional and policy-gated, and reuse secret-like/size checks before writing curated raw copies. [VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/raw/README.md; VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:463-530] |
| INGEST-02 | Ingest updates existing wiki pages before creating new pages. [VERIFIED: .planning/REQUIREMENTS.md] | The ingest protocol should read `index.md`, inspect candidate existing pages, and require explicit "no existing page covers this" rationale before new page creation. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md] |
| INGEST-03 | Ingest creates a summary page only when a source affects multiple wiki areas or cross-cutting project knowledge. [VERIFIED: .planning/REQUIREMENTS.md] | Use the Phase 4 blast-radius rule: 1-3 pages for narrow sources, 5-10 for cross-cutting, hard cap 15. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md] |
| INGEST-04 | Ingest adds provenance to touched pages and updates `.llm-wiki/index.md` and `.llm-wiki/log.md`. [VERIFIED: .planning/REQUIREMENTS.md] | Add a provenance note to each touched durable page, append a concise log entry, and update `index.md` only for newly created pages. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md] |
| INGEST-05 | Ingest keeps active task state, execution checkpoints, and unvalidated work out of `.llm-wiki/`. [VERIFIED: .planning/REQUIREMENTS.md] | The raw and log policies must reject full transcripts, full logs, dumps, secrets, private data, and active task state. [VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/raw/README.md; VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/log.md] |
| TEST-03 | Query against seeded pages returns wiki-cited answers and appends `.llm-wiki/log.md`. [VERIFIED: .planning/REQUIREMENTS.md] | Test deterministic evidence/log support plus the documented agent answer contract; avoid a Python-only final-answer generator because D-07 forbids it. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md] |
</phase_requirements>

## Project Constraints (from AGENTS.md)

- The project must initialize and operate `.llm-wiki/` inside the actual Git root, not a multi-repo parent directory. [VERIFIED: AGENTS.md; VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:134-145]
- Current repository files are authoritative when they disagree with `.llm-wiki/`. [VERIFIED: AGENTS.md; VERIFIED: skills/project-llm-wiki/SKILL.md]
- `.llm-wiki/` stores curated, validated, non-secret durable knowledge; volatile workflow state belongs in `.planning/`, Linear, OMX, or workflow files. [VERIFIED: AGENTS.md; VERIFIED: .planning/PROJECT.md]
- Keep the implementation simple: prefer Markdown templates plus small Python standard-library scripts and do not add dependencies unless a later phase explicitly changes the constraint. [VERIFIED: AGENTS.md; VERIFIED: skills/project-llm-wiki/references/testing.md]
- Verify package changes with `python3 -m unittest discover -s skills/project-llm-wiki/tests`. [VERIFIED: skills/project-llm-wiki/SKILL.md; VERIFIED: skills/project-llm-wiki/references/testing.md]
- Do not edit `AGENTS.md` in Phase 4; AGENTS patching belongs to Phase 5. [VERIFIED: .planning/ROADMAP.md; VERIFIED: user request]
- No project-local `.codex/skills/` or `.agents/skills/` directories were available during research. [VERIFIED: `find .codex/skills .agents/skills -maxdepth 3 -name SKILL.md`]
- No `.planning/graphs/graph.json` file was present, so no graph context was available. [VERIFIED: `ls .planning/graphs/graph.json`]
- The canonical personal vault references under `/Users/huangchihan/Documents/markdowns/...` could not be read from this runtime even after an escalated read attempt; the Phase 4 `CONTEXT.md` summaries are therefore the project-local source used for those patterns. [VERIFIED: failed `sed -n` reads returned `Operation not permitted`; VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]

## Summary

Phase 4 should implement a repo-local compounding loop without turning the Python helper into an LLM. Query is agent-protocol-first: the skill must instruct the agent to read `.llm-wiki/index.md` first, inspect relevant pages, answer with `[[wikilink]]` citations, label inference separately, and append a concise log entry. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md] The helper should support this with deterministic discovery, citation-page formatting, not-covered templates, and log append primitives. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:260-330,793-831]

Ingest should update durable compiled pages first and treat `.llm-wiki/raw/curated/` as optional evidence retention, not a dump location. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md; VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/raw/README.md] The planner should build ingest as a guided protocol plus deterministic helper primitives: source normalization, source safety checks, candidate page discovery, page write helpers, provenance insertion, index update for new pages, and log append. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:227-232,260-330,463-530,793-831]

**Primary recommendation:** Plan Phase 4 as three slices: query protocol plus log helper, curated ingest protocol plus safe file/index/provenance helpers, then fixtures proving index-first query, wikilink-cited evidence, log append, existing-page-first ingest, raw policy enforcement, and no active task state in `.llm-wiki/`. [VERIFIED: .planning/ROADMAP.md; VERIFIED: .planning/REQUIREMENTS.md]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| Query answer synthesis | Agent protocol | `.llm-wiki/` Markdown | D-06 and D-07 lock query as agent-protocol-first and prohibit deterministic Python final-answer generation. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md] |
| Query page discovery | Local CLI helper | Agent protocol | The helper can safely read `index.md`, normalize wikilinks, and identify candidate pages without synthesizing the final answer. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:319-330] |
| Query log append | Local CLI helper | Agent protocol | Log append is deterministic text I/O and should use a reusable helper so every query has the same shape. [VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/log.md] |
| Ingest source interpretation | Agent protocol | Local CLI helper | Deciding durable knowledge and target pages is semantic; helper primitives can normalize inputs and enforce filesystem/raw policy. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md] |
| Ingest writes to `.llm-wiki/` | Local CLI helper | Agent protocol | Writing files, preserving repo boundary, avoiding symlink escape, and appending provenance are deterministic operations already patterned in the helper. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:227-232,737-767] |
| URL source handling | Local CLI helper | Agent protocol | URL support is allowed, but raw persistence remains policy-gated and video URLs require curated text or an external adapter. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md; CITED: https://docs.python.org/3/library/urllib.request.html] |
| Raw safety checks | Local CLI helper | Existing lint helpers | Phase 3 already has high-confidence secret-like and raw-size checks that Phase 4 should reuse before preserving curated raw copies. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:463-530] |
| Regression validation | Python unittest suite | Temporary Git repos | Existing tests use subprocess execution against temporary Git repositories; Phase 4 should continue that shape. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_init.py; CITED: https://docs.python.org/3/library/unittest.html] |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python standard library | Local `python3` is 3.14.3. [VERIFIED: `python3 --version`] | CLI helper, text/file operations, URL adapter, and tests. | The project contract is standard-library only for v1. [VERIFIED: AGENTS.md; VERIFIED: skills/project-llm-wiki/references/testing.md] |
| `argparse` | Python 3.14 stdlib. [CITED: https://docs.python.org/3/library/argparse.html] | Extend `query` and `ingest` subcommands with clear flags. | Existing helper uses `argparse` subcommands and `set_defaults`. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:942-984] |
| `pathlib` | Python 3.14 stdlib. [CITED: https://docs.python.org/3/library/pathlib.html] | Keep path joins, relative paths, symlink checks, and file writes explicit. | Existing helper uses `Path` and `PurePosixPath` for wiki paths and wikilinks. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:13-45,227-232,323-330] |
| `subprocess` | Python 3.14 stdlib. [CITED: https://docs.python.org/3/library/subprocess.html] | Preserve Git-root resolution via `git rev-parse --show-toplevel`. | The current helper already uses this repository boundary. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:134-145; CITED: https://git-scm.com/docs/git-rev-parse] |
| `re` | Python 3.14 stdlib. [CITED: https://docs.python.org/3/library/re.html] | Reuse wikilink extraction, frontmatter-ish matches, and safety patterns. | Phase 3 implemented deterministic regex helpers without dependencies. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:46-77] |
| `datetime` | Python 3.14 stdlib. [CITED: https://docs.python.org/3/library/datetime.html] | Write ISO-date query and ingest log/provenance entries. | Existing lint staleness already uses ISO dates. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:533-582] |
| `urllib.request` and `urllib.parse` | Python 3.14 stdlib. [CITED: https://docs.python.org/3/library/urllib.request.html] | Optional bounded URL text fetch or URL provenance normalization. | Phase 4 locks URL source support while keeping no third-party dependencies. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md] |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `json` | Python 3.14 stdlib. [CITED: https://docs.python.org/3/library/json.html] | Optional parseable query evidence and ingest preview output. | Use if the planner adds `--json` for agent tooling, matching lint's parseable output style. [VERIFIED: skills/project-llm-wiki/references/command-surface.md:23-45] |
| `unittest` | Python 3.14 stdlib. [CITED: https://docs.python.org/3/library/unittest.html] | Fixture tests for query and ingest behavior. | Continue existing test discovery and subprocess style. [VERIFIED: skills/project-llm-wiki/references/testing.md] |
| `tempfile` | Python 3.14 stdlib. [CITED: https://docs.python.org/3/library/tempfile.html] | Isolated Git repos and local fixture files. | Existing tests use temporary Git repos. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_init.py] |
| Git CLI | Local Git is 2.50.1. [VERIFIED: `git --version`] | Resolve actual repo root. | Required by earlier phases and current helper behavior. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:134-145] |
| ripgrep | Local ripgrep is 15.1.0. [VERIFIED: `rg --version`] | Developer inspection only. | Do not make runtime behavior depend on `rg`; runtime remains Python stdlib plus Git. [VERIFIED: skills/project-llm-wiki/references/testing.md] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Index-first Markdown discovery | Vector database or qmd | Embeddings/vector search are explicitly deferred until the index stops being enough. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md; CITED: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f] |
| Agent-protocol answer synthesis | Python-generated final answers | Python final-answer generation conflicts with D-07 and would be brittle for inference/citation boundaries. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md] |
| Stdlib URL handling | `requests`, newspaper parsers, browser automation | Third-party URL extractors would violate the no-dependency constraint and increase raw-copy risk. [VERIFIED: AGENTS.md; CITED: https://docs.python.org/3/library/urllib.request.html] |
| Explicit source-size blast radius | Update every matched page | Context locks a 15-page hard cap and existing-page-first updates to avoid noisy wiki churn. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md] |

**Installation:**

No package installation is required for Phase 4. [VERIFIED: skills/project-llm-wiki/references/testing.md]

```bash
python3 -m unittest discover -s skills/project-llm-wiki/tests
```

**Version verification:** No npm packages are recommended. Local probes returned `Python 3.14.3`, `git version 2.50.1 (Apple Git-155)`, and `ripgrep 15.1.0`. [VERIFIED: `python3 --version`; VERIFIED: `git --version`; VERIFIED: `rg --version`]

## Architecture Patterns

### System Architecture Diagram

```text
Query flow
User question
  |
  v
project-wiki-query skill protocol
  |
  v
read .llm-wiki/index.md first
  |
  v
extract candidate [[wikilinks]]
  |
  +-- no relevant pages -> not-covered answer -> append query log
  |
  v
agent reads relevant wiki pages
  |
  v
answer:
  - direct claims with [[wikilink]] citations
  - optional labeled inference section
  |
  v
append concise log.md entry

Ingest flow
Curated text/file/URL source
  |
  v
validate source boundary and raw policy
  |
  v
read index.md and existing pages first
  |
  v
choose target pages within blast radius
  |
  +-- existing page covers concept -> update existing page + provenance
  +-- no existing coverage -> create new durable page + index entry
  |
  v
optionally preserve short curated raw note
  |
  v
append ingest log with pages touched and key ideas
```

This keeps semantic decisions in the agent protocol while leaving repo-boundary, path, log, provenance, index, and safety mechanics in deterministic helper code. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md; VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py]

### Recommended Project Structure

```text
skills/project-llm-wiki/
+-- SKILL.md                         # Query and ingest protocols
+-- scripts/
|   +-- project_wiki.py              # query/ingest helpers, log/provenance utilities
+-- tests/
|   +-- test_project_wiki_query.py   # new Phase 4 query fixtures
|   +-- test_project_wiki_ingest.py  # new Phase 4 ingest fixtures
|   +-- existing tests
+-- references/
|   +-- command-surface.md           # implemented query/ingest contract
|   +-- testing.md                   # Phase 4 validation commands
+-- assets/templates/llm-wiki/
    +-- index.md
    +-- log.md
    +-- raw/
```

This structure matches the existing package-owned script, reference, template, and test layout. [VERIFIED: `rg --files skills/project-llm-wiki`; VERIFIED: skills/project-llm-wiki/references/testing.md]

### Pattern 1: Query Is a Protocol, Not a Python Answer Bot

**What:** Update `SKILL.md` and `references/command-surface.md` so `project-wiki-query` requires index-first reading, relevant page inspection, direct-claim wikilink citations, labeled inference, not-covered handling, and log append. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]  
**When to use:** Use for every user query against `.llm-wiki/`. [VERIFIED: .planning/REQUIREMENTS.md]  
**Helper role:** The helper may output candidate pages, evidence packet metadata, and a log-entry skeleton; it should not claim to answer semantic questions independently. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]

### Pattern 2: Consistent Append-Only Log Entries

**What:** Use one helper for query and ingest log entries with consistent headings and bounded fields. [VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/log.md]  
**When to use:** Append after each completed query or ingest. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]  
**Recommended shape:**

```markdown
## [2026-05-13] query | concise question summary
- Pages consulted: [[index]], [[features/ideas]]
- Key insight: concise cited answer summary or not-covered result.
```

Karpathy's LLM Wiki pattern recommends a chronological `log.md` and notes that consistent prefixes make the log parseable with simple tools. [CITED: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f]

### Pattern 3: Source Input Normalization

**What:** Normalize text, file, and URL sources into a small internal source record with fields such as `kind`, `title`, `provenance`, `text`, `raw_copy_allowed`, and `suggested_filename`. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]  
**When to use:** Run before any ingest write. [VERIFIED: .planning/REQUIREMENTS.md]  
**Control:** For file inputs, require repo-root-confined or explicitly supplied files and read as UTF-8; for URL inputs, preserve the URL as provenance and fetch only through a bounded adapter if the planner chooses to implement one. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:227-232,303-316; CITED: https://docs.python.org/3/library/urllib.request.html]

### Pattern 4: Existing-Page-First Update Plan

**What:** Build an ingest plan before writing: candidate existing pages, pages to update, optional new pages, optional raw curated copy, index changes, and log entry. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]  
**When to use:** Use for every ingest, even if implementation writes immediately after constructing the plan. [VERIFIED: .planning/REQUIREMENTS.md]  
**Guardrail:** New pages require a rationale that no existing page covers the concept or that multiple pages now reference the concept. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]

### Pattern 5: Provenance Is Per Touched Page

**What:** Add a short provenance note to every durable page touched by ingest. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]  
**When to use:** Append near a page's source/provenance section if present, otherwise add a concise `## Provenance` section. [ASSUMED]  
**Example wording:** `Updated from Source Title, 2026-05-13.` [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]

### Anti-Patterns to Avoid

- **Python semantic answer generation:** D-07 says Phase 4 should not hard-code answer generation into deterministic Python logic. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]
- **Raw dump ingestion:** Full transcripts, full logs, dumps, secrets, private data, and large unreviewed material are disallowed. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md; VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/raw/README.md]
- **Creating isolated new notes first:** The key ingest value is strengthening existing compiled pages before creating new pages. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]
- **Logging full Q&A transcripts:** `log.md` is an operational timeline, not chat history. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]
- **Depending on `$watch-video`:** This user's local preprocessing skill may help this user, but Project LLM Wiki core ingest must stay adapter-agnostic. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]
- **Trusting wiki over repo:** Existing project instructions say current repo files win when wiki notes disagree. [VERIFIED: AGENTS.md; VERIFIED: .planning/PROJECT.md]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Semantic final answers in Python | Keyword-to-answer templates or deterministic synthesis | Agent protocol plus deterministic candidate/evidence helpers | D-07 explicitly keeps final answer generation out of Python. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md] |
| Vector/RAG search | Embedding database, qmd integration, or local vector store | Index-first page discovery and simple helper search | Vector search is deferred; the LLM Wiki pattern says `index.md` is enough at moderate scale. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md; CITED: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f] |
| Full web/article extraction | HTML readability parser, headless browser, or third-party scraper | URL provenance plus bounded stdlib URL text adapter only if needed | URL ingest must stay no-dependency and raw-policy-gated. [VERIFIED: AGENTS.md; VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md] |
| Secret scanning platform | Provider API validation or entropy scanner | Reuse Phase 3 high-confidence secret-like lint helpers | Phase 4 should preserve raw policy without adding dependencies. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:497-530] |
| Markdown AST editor | Full parser and structural rewriter | Conservative append/update helpers with explicit sections | Existing templates are simple Markdown and Phase 4 scope is bounded to wiki pages, index, raw curated notes, and log. [VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/index.md; VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/log.md] |

**Key insight:** The hard part is not file I/O; it is preserving the knowledge boundary. The helper should make safe file changes easy, while the agent protocol remains responsible for deciding what knowledge belongs in durable wiki pages. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]

## Common Pitfalls

### Pitfall 1: Letting Tests Force a Python Answer Generator
**What goes wrong:** TEST-03 is interpreted as requiring Python to generate final cited answers. [VERIFIED: .planning/REQUIREMENTS.md]  
**Why it happens:** The requirement says query returns cited answers, while D-07 forbids deterministic Python answer generation. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]  
**How to avoid:** Test the documented agent answer contract plus deterministic helper evidence/log behavior; if the planner needs a CLI output, label it as evidence/protocol output rather than final synthesis. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]  
**Warning signs:** `project_wiki.py` starts producing prose conclusions without reading all cited pages through the agent protocol. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py]

### Pitfall 2: Storing Raw URLs or Transcripts as Knowledge
**What goes wrong:** Ingest stores large fetched pages, video transcripts, logs, or private material under `.llm-wiki/raw/curated/`. [VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/raw/README.md]  
**Why it happens:** URL/video input gets treated as raw material instead of curated source material. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]  
**How to avoid:** Treat stable URLs as provenance unless the curated text is short, important, unstable, user-provided, adapter-generated, or needed for future verification. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]  
**Warning signs:** Raw files over 100 KB or raw files containing secret-like content. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:463-530]

### Pitfall 3: Updating `index.md` Too Often
**What goes wrong:** Every edit to an existing page churns `index.md`. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]  
**Why it happens:** Ingest treats the index as a change log. [VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/index.md]  
**How to avoid:** Update `index.md` only when creating a newly indexed durable page. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]  
**Warning signs:** Existing-page-only ingests produce unrelated index diffs. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]

### Pitfall 4: Blurring Durable Knowledge and Task State
**What goes wrong:** Ingest writes active task status, checkpoints, or unvalidated work into `.llm-wiki/`. [VERIFIED: .planning/REQUIREMENTS.md]  
**Why it happens:** The log is mistaken for a session transcript or GSD state store. [VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/log.md]  
**How to avoid:** Keep log entries short and durable; keep plans, checkpoints, and active state in `.planning/`, Linear, OMX, or workflow files. [VERIFIED: AGENTS.md; VERIFIED: .planning/PROJECT.md]  
**Warning signs:** `log.md` contains full prompts, full answers, todo lists, or execution checkpoints. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]

### Pitfall 5: URL Fetch Security Drift
**What goes wrong:** URL support can become SSRF-like local resource access or can persist unsafe fetched content. [CITED: https://owasp.org/www-project-application-security-verification-standard/]  
**Why it happens:** The helper accepts arbitrary schemes or reads network content without bounds. [CITED: https://docs.python.org/3/library/urllib.request.html]  
**How to avoid:** If URL fetching is implemented, allow only `http` and `https`, reject localhost/private/file schemes, cap bytes, decode as text only, and require raw-policy checks before persistence. [ASSUMED]  
**Warning signs:** Support for `file://`, localhost URLs, unbounded reads, binary downloads, or automatic raw writes. [ASSUMED]

## Code Examples

Verified patterns from current repo and official docs:

### Log Append Helper

```python
# Source: skills/project-llm-wiki/assets/templates/llm-wiki/log.md
# Source: https://docs.python.org/3/library/datetime.html
def append_log_entry(git_root, action, title, pages, key_insight):
    log_path = git_root / ".llm-wiki" / "log.md"
    today = datetime.date.today().isoformat()
    linked_pages = ", ".join(pages) if pages else "(none)"
    entry = "\n".join(
        [
            "",
            f"## [{today}] {action} | {title}",
            f"- Pages consulted: {linked_pages}",
            f"- Key insight: {key_insight}",
            "",
        ]
    )
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(entry)
```

### Index-First Candidate Discovery

```python
# Source: skills/project-llm-wiki/scripts/project_wiki.py:319-330
def candidate_pages_from_index(index_text):
    pages = []
    for raw_target in extract_wikilinks(index_text):
        normalized = normalize_wikilink_target(raw_target)
        if normalized:
            pages.append(pathlib.Path(".llm-wiki") / normalized)
    return pages
```

### Source Record Boundary

```python
# Source: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md
def make_source_record(kind, title, provenance, text):
    return {
        "kind": kind,
        "title": title.strip(),
        "provenance": provenance.strip(),
        "text": text,
        "raw_copy_allowed": False,
    }
```

### Path Containment Before Writes

```python
# Source: skills/project-llm-wiki/scripts/project_wiki.py:227-232
def safe_wiki_path(git_root, wiki_relative_path):
    wiki_root = git_root / ".llm-wiki"
    target = wiki_root / wiki_relative_path
    if target.is_symlink() or not path_is_under(target, wiki_root):
        raise ValueError("target must stay inside .llm-wiki")
    return target
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Re-derive answers from raw documents on every query | Maintain a compiled, interlinked Markdown wiki that gets richer over time | Karpathy gist published 2026-04-04. [CITED: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f] | Phase 4 should update existing durable pages during ingest instead of treating raw sources as the primary retrieval layer. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md] |
| Query raw sources directly | Read `index.md`, then relevant wiki pages, then answer with citations | Phase 4 locked this as D-06. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md] | The query protocol must prove index-first behavior. [VERIFIED: .planning/REQUIREMENTS.md] |
| Keep full query chats in history | Append concise log entries with consistent prefixes | Karpathy pattern recommends chronological logs; Phase 4 locks concise log entries. [CITED: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f; VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md] | `log.md` should stay parseable and durable. [VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/log.md] |
| Store every raw source | Preserve raw curated copies only when policy says they are useful and safe | Phase 4 locked raw curated copy policy. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md] | Stable external URLs can be provenance-only. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md] |

**Deprecated/outdated:**
- Treating Phase 4 as a RAG/vector-search build is out of scope; embeddings and qmd-style search are deferred. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]
- Treating YouTube/video URLs as core ingest inputs is out of scope unless preprocessed into curated text by an adapter. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | If URL fetching is implemented, it should allow only `http` and `https`, reject localhost/private/file schemes, cap bytes, decode as text only, and require raw-policy checks before persistence. | Common Pitfalls / Security Domain | Planner may over-scope URL support or under-specify URL safety. |
| A2 | Provenance notes can be appended under an existing provenance/source section if present, otherwise under a new `## Provenance` section. | Architecture Patterns | Page formatting may drift if the user prefers a different page schema. |

## Open Questions

1. **How should TEST-03 phrase the query fixture without violating D-07?**
   - What we know: The requirement says query returns wiki-cited answers and appends log; D-07 says Python must not hard-code final answer generation. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]
   - What's unclear: Whether the fixture should assert the agent protocol text, deterministic evidence output, or a conservative non-synthetic answer template. [ASSUMED]
   - Recommendation: Test deterministic evidence/log support and the documented answer contract; do not test Python semantic synthesis. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]

2. **Should URL ingest fetch remote content or only accept URL provenance plus curated text?**
   - What we know: URL sources are in scope, but raw policy forbids unsafe, uncurated, secret-bearing, private, or oversized material. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]
   - What's unclear: Whether Phase 4 should implement a bounded `urllib` fetch adapter or defer real fetching to user/agent preprocessing. [ASSUMED]
   - Recommendation: Implement URL provenance support and optional bounded text fetch only if the planner can keep tests local and safety controls simple. [ASSUMED]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python 3 | Helper and tests | Yes | 3.14.3 [VERIFIED: `python3 --version`] | None needed |
| Git CLI | Git-root resolution | Yes | 2.50.1 Apple Git-155 [VERIFIED: `git --version`] | No fallback; Git root is a project contract |
| ripgrep | Research/developer inspection | Yes | 15.1.0 [VERIFIED: `rg --version`] | Python/stdlib file traversal |
| Network access | Optional URL fetch adapter | Restricted in coding sandbox [VERIFIED: developer environment] | N/A | Use file/text fixtures and URL provenance-only ingest |
| Project-local skills | Project-specific skill conventions | No | N/A [VERIFIED: missing `.codex/skills` and `.agents/skills`] | Use package skill under `skills/project-llm-wiki/` |

**Missing dependencies with no fallback:**
- None for the standard-library Phase 4 plan. [VERIFIED: skills/project-llm-wiki/references/testing.md]

**Missing dependencies with fallback:**
- External network fetch should not block planning; URL support can be tested with provenance-only inputs or a local fixture server if implemented. [ASSUMED]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python `unittest` stdlib. [CITED: https://docs.python.org/3/library/unittest.html] |
| Config file | None. [VERIFIED: skills/project-llm-wiki/references/testing.md] |
| Quick run command | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_query.py` [ASSUMED] |
| Full suite command | `python3 -m unittest discover -s skills/project-llm-wiki/tests` [VERIFIED: skills/project-llm-wiki/references/testing.md] |
| Current full suite status | 77 tests passed during research. [VERIFIED: `python3 -m unittest discover -s skills/project-llm-wiki/tests`] |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| QUERY-01 | Query reads `index.md` before individual pages | unit/subprocess | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_query.py` | No - Wave 0 |
| QUERY-02 | Answer contract requires `[[wikilink]]` citations | unit/doc/protocol | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_query.py` | No - Wave 0 |
| QUERY-03 | Not-covered answer lists consulted pages and suggests ingest source type | unit/subprocess | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_query.py` | No - Wave 0 |
| QUERY-04 | Query appends concise `log.md` entry | unit/subprocess | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_query.py` | No - Wave 0 |
| INGEST-01 | Curated source ingest preserves raw policy | unit/subprocess | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_ingest.py` | No - Wave 0 |
| INGEST-02 | Ingest updates existing pages before creating new pages | unit/subprocess | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_ingest.py` | No - Wave 0 |
| INGEST-03 | Summary pages only for cross-cutting sources | unit/subprocess | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_ingest.py` | No - Wave 0 |
| INGEST-04 | Ingest adds provenance, updates index/log | unit/subprocess | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_ingest.py` | No - Wave 0 |
| INGEST-05 | Ingest excludes active task state and unsafe raw material | unit/subprocess | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_ingest.py` | No - Wave 0 |
| TEST-03 | Seeded query proves cited output and log append behavior | unit/subprocess/protocol | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_query.py` | No - Wave 0 |

### Sampling Rate

- **Per task commit:** targeted query or ingest test file plus package import whitelist if imports changed. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py]
- **Per wave merge:** `python3 -m unittest discover -s skills/project-llm-wiki/tests`. [VERIFIED: skills/project-llm-wiki/references/testing.md]
- **Phase gate:** Full suite green before `$gsd-verify-work`. [VERIFIED: .planning/config.json]

### Wave 0 Gaps

- [ ] `skills/project-llm-wiki/tests/test_project_wiki_query.py` - covers QUERY-01 through QUERY-04 and TEST-03. [VERIFIED: .planning/REQUIREMENTS.md]
- [ ] `skills/project-llm-wiki/tests/test_project_wiki_ingest.py` - covers INGEST-01 through INGEST-05. [VERIFIED: .planning/REQUIREMENTS.md]
- [ ] Update `skills/project-llm-wiki/references/testing.md` with Phase 4 targeted commands. [VERIFIED: skills/project-llm-wiki/references/testing.md]
- [ ] Update import whitelist if `urllib.request`, `urllib.parse`, or other stdlib modules are added. [VERIFIED: skills/project-llm-wiki/tests/test_project_wiki_package.py]

## Security Domain

### Applicable ASVS Categories

OWASP lists ASVS 5.0.0 as the latest stable release and recommends versioned requirement references because identifiers can change. [CITED: https://owasp.org/www-project-application-security-verification-standard/]

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V1 Encoding and Sanitization | Yes | Escape or reject unsafe text only in downstream contexts; avoid shell interpolation by using argument lists for subprocess calls. [CITED: https://owasp.org/www-project-application-security-verification-standard/; VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:134-145] |
| V2 Validation and Business Logic | Yes | Validate source kind, URL scheme, page path, raw size, and existing-page-first ingest rules. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md] |
| V5 File Handling | Yes | Keep writes under `.llm-wiki/`, reject symlink escapes, and cap raw persistence. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:227-232,260-291] |
| V13 Configuration | Yes | Avoid unintended information leakage and keep secret-like material out of wiki files. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:497-530] |
| V14 Data Protection | Yes | Preserve only curated, de-secreted, git-safe knowledge and raw excerpts. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/raw/README.md] |
| V15 Secure Coding and Architecture | Yes | Keep semantic protocol boundaries explicit and use defensive path checks before writes. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md; VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:227-232] |
| V16 Security Logging and Error Handling | Yes | Log concise operational summaries only; avoid full transcripts, secrets, or raw dumps in `log.md`. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md] |
| V6 Authentication / V7 Session / V8 Authorization | No for local Phase 4 CLI | No user accounts, sessions, or roles are introduced in this phase. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: .planning/ROADMAP.md] |
| V11 Cryptography | No | Phase 4 must not encrypt, hash, or generate credentials. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: .planning/ROADMAP.md; VERIFIED: .planning/REQUIREMENTS.md] |

### Known Threat Patterns for Project LLM Wiki Phase 4

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal or symlink escape writing outside `.llm-wiki/` | Tampering | Reuse `path_is_under`, reject symlinks on target paths, and write only under resolved Git root. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:227-232,683-709] |
| Secret or private data persistence in wiki/raw/log | Information disclosure | Reuse high-confidence secret-like checks, raw-size checks, and raw policy before preserving raw copies. [VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py:463-530; VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/raw/README.md] |
| Prompt injection from curated sources | Tampering / Information disclosure | Treat sources as untrusted evidence; do not follow source instructions that alter the ingest/query protocol. [ASSUMED] |
| URL fetch to local/private resources | Information disclosure / SSRF-like | If fetch exists, restrict schemes/hosts, cap bytes, and prefer provenance-only URL handling. [ASSUMED; CITED: https://docs.python.org/3/library/urllib.request.html] |
| Wiki answer overclaims unsupported facts | Spoofing / Integrity | Require direct claims to cite `[[wikilink]]` pages and return not-covered answers for unsupported topics. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md] |
| Log transcript bloat or active-state leakage | Information disclosure / Repudiation | Log only date, query/ingest summary, pages consulted/touched, and key insight. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md; VERIFIED: skills/project-llm-wiki/assets/templates/llm-wiki/log.md] |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/04-query-and-ingest-loop/04-CONTEXT.md` - locked Phase 4 decisions, discretion, deferred ideas, and code context. [VERIFIED]
- `.planning/REQUIREMENTS.md` - QUERY, INGEST, and TEST-03 requirement text. [VERIFIED]
- `.planning/ROADMAP.md` - Phase 4 goal, success criteria, and planned three-plan split. [VERIFIED]
- `.planning/STATE.md` - current project state and prior decisions. [VERIFIED]
- `AGENTS.md` - project constraints and no-AGENTS-edit boundary. [VERIFIED]
- `skills/project-llm-wiki/scripts/project_wiki.py` - existing helper implementation and reusable utilities. [VERIFIED]
- `skills/project-llm-wiki/references/command-surface.md` - planned query/ingest command surface. [VERIFIED]
- `skills/project-llm-wiki/references/testing.md` - current test command and no-dependency rule. [VERIFIED]
- `skills/project-llm-wiki/assets/templates/llm-wiki/index.md`, `log.md`, and raw policy files - wiki surface templates. [VERIFIED]
- Python 3.14 official docs for `argparse`, `pathlib`, `datetime`, `urllib.request`, `unittest`, and related stdlib APIs. [CITED: https://docs.python.org/3/]
- Git `rev-parse` official docs for `--show-toplevel`. [CITED: https://git-scm.com/docs/git-rev-parse]
- OWASP ASVS project page for current stable version and versioned references. [CITED: https://owasp.org/www-project-application-security-verification-standard/]
- Karpathy `llm-wiki` gist for compiled wiki, index/log, and ingest/query concepts. [CITED: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f]

### Secondary (MEDIUM confidence)

- OWASP Developer Guide ASVS overview for general usage context. [CITED: https://devguide.owasp.org/en/03-requirements/05-asvs/]
- OWASP Cheat Sheet ASVS index for ASVS 5.0.x topical/category mapping. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html]

### Tertiary (LOW confidence)

- Personal vault references from `Documents/markdowns` were not directly readable in this runtime; only the Phase 4 context summaries of them were used. [VERIFIED: failed sandbox read; VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - no third-party dependencies are required and current local versions were probed. [VERIFIED: `python3 --version`; VERIFIED: `git --version`; VERIFIED: skills/project-llm-wiki/references/testing.md]
- Architecture: HIGH - Phase 4 context locks query as agent-protocol-first and ingest as existing-page-first; current helper already provides repo-boundary and Markdown utilities. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md; VERIFIED: skills/project-llm-wiki/scripts/project_wiki.py]
- Pitfalls: MEDIUM - most pitfalls come from locked project decisions; URL fetch safety and prompt-injection controls are inferred from standard security practice and marked assumed where not project-locked. [VERIFIED: .planning/phases/04-query-and-ingest-loop/04-CONTEXT.md; ASSUMED]

**Research date:** 2026-05-13  
**Valid until:** 2026-06-12 for repo-local implementation patterns; re-check external security guidance and Python/Git docs before changing URL fetch behavior. [ASSUMED]
