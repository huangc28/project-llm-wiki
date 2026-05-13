# Phase 3: Lint and Safety Checks - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-13
**Phase:** 03-lint-and-safety-checks
**Areas discussed:** Wikilink and Index Rules, Safety and Size Heuristics, Staleness and Contradiction Warnings, CLI Report Shape

---

## Wikilink and Index Rules

| Option | Description | Selected |
|--------|-------------|----------|
| WikiLinks only | Lint Obsidian `[[path]]` links because templates already use that convention. | yes |
| WikiLinks + Markdown | Also lint relative Markdown links. | |
| You decide | Let planning choose the simplest rule. | |

**User's choice:** WikiLinks only.
**Notes:** User plans to open the wiki in Obsidian, so Obsidian-style wikilinks are the primary link format.

| Option | Description | Selected |
|--------|-------------|----------|
| Only main wiki pages | Require main wiki pages to be discoverable from `index.md`; exclude `raw/curated/`. | yes |
| All `.llm-wiki` pages | Require every page, including raw sources, to be indexed. | |
| Existing links only | Only validate links already written in `index.md`. | |

**User's choice:** Only main wiki pages.
**Notes:** `raw/curated/` is supporting source material and should not be forced into top-level navigation.

| Option | Description | Selected |
|--------|-------------|----------|
| Broken links as error | Missing linked wiki pages fail lint. | yes |
| Broken links as warning | Report missing linked wiki pages without failing. | |
| Severity by location | Use different severity by directory. | |

**User's choice:** Broken links as error.
**Notes:** A brand-new standalone topic page is allowed to have no outgoing links, but it should be indexed if it is a main wiki page.

| Option | Description | Selected |
|--------|-------------|----------|
| Support common Obsidian forms | Support `[[path]]`, `[[path.md]]`, `[[path\|Alias]]`, and `[[path#Heading]]` for page existence. | yes |
| Only simplest wikilinks | Only support `[[path]]`. | |
| Also validate headings | Validate heading fragments too. | |

**User's choice:** Support common Obsidian forms.
**Notes:** Alias text and heading fragments are ignored in Phase 3; only the page existence is checked.

---

## Safety and Size Heuristics

| Option | Description | Selected |
|--------|-------------|----------|
| High-confidence patterns only | Detect patterns likely to be real secrets. | yes |
| High-confidence plus common sensitive words | Also warn on words like secret/token/credential. | |
| Very strict | Warn on broad suspicious text. | |

**User's choice:** High-confidence patterns only.
**Notes:** Avoid noisy documentation false positives.

| Option | Description | Selected |
|--------|-------------|----------|
| Scan all `.llm-wiki` | Secrets should not appear anywhere in the wiki. | yes |
| Scan only `.llm-wiki/raw` | Narrow scan to the highest-risk area. | |
| Raw strict, other pages light | Mixed rule. | |

**User's choice:** Scan all `.llm-wiki`.
**Notes:** The raw policy forbids unsafe material everywhere in the wiki.

| Option | Description | Selected |
|--------|-------------|----------|
| Raw only | Apply file-size warnings only to `.llm-wiki/raw/`. | yes |
| All `.llm-wiki` | Warn on any large wiki page. | |
| No size check | Skip size warnings. | |

**User's choice:** Raw only.
**Notes:** Size checks prevent raw dumps/logs from entering git-tracked wiki content without penalizing legitimate long wiki pages.

| Option | Description | Selected |
|--------|-------------|----------|
| 100 KB | Warn on raw files over 100 KB. | yes |
| 500 KB | Warn on larger raw files only. | |
| 1 MB | Warn only on very large raw files. | |

**User's choice:** 100 KB.
**Notes:** This is intended to catch full logs, dumps, and large generated output early.

| Option | Description | Selected |
|--------|-------------|----------|
| Warning only | Secret-looking findings do not fail lint. | yes |
| Error | Secret-looking findings fail lint. | |
| High-confidence error, others warning | Mixed severity. | |

**User's choice:** Warning only.
**Notes:** Phase 3 is not a complete secret scanner; findings should be visible but not blocking.

---

## Staleness and Contradiction Warnings

| Option | Description | Selected |
|--------|-------------|----------|
| Frontmatter `updated:` only | Use explicit page metadata. | yes |
| Warn when `updated:` is missing | Push every page to add metadata. | |
| Git/file modified time | Use filesystem or Git timestamps. | |

**User's choice:** Frontmatter `updated:` only.
**Notes:** Lint does not auto-modify stale pages. A user or agent must review content against current repo files before updating `updated:`.

| Option | Description | Selected |
|--------|-------------|----------|
| 90 days | Warn when `updated:` is older than 90 days. | yes |
| 30 days | More aggressive warning cadence. | |
| 180 days | More relaxed warning cadence. | |

**User's choice:** 90 days.
**Notes:** Pages without `updated:` are not stale-checked in Phase 3.

| Option | Description | Selected |
|--------|-------------|----------|
| Repo path drift only | Warn when explicitly referenced repo paths do not exist. | yes |
| Semantic contradiction scanning | Try to detect text/code disagreement. | |
| No contradiction warning | Skip contradiction-related checks. | |

**User's choice:** Repo path drift only.
**Notes:** No AI semantic contradiction detection in Phase 3.

| Option | Description | Selected |
|--------|-------------|----------|
| Code spans and code blocks | Inspect backticked paths only. | yes |
| Scan all text | Search ordinary prose for path-like strings. | |
| Only frontmatter refs | Require explicit metadata. | |

**User's choice:** Code spans and code blocks.
**Notes:** This keeps false positives low by checking only intentionally marked path references.

| Option | Description | Selected |
|--------|-------------|----------|
| Warning | Missing repo path references are warning findings. | yes |
| Error | Missing repo path references fail lint. | |
| Error only when clearly repo-local | Mixed severity. | |

**User's choice:** Warning.
**Notes:** Missing paths may be examples, future paths, or external paths.

---

## CLI Report Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Only errors exit 1 | Warning-only lint exits 0. | yes |
| Any warning or error exits 1 | Warnings fail lint too. | |
| Always exit 0 | Report only; never fail. | |

**User's choice:** Only errors exit 1.
**Notes:** Broken wikilinks fail; warning-only findings stay non-blocking.

| Option | Description | Selected |
|--------|-------------|----------|
| Human-readable default plus optional JSON | Text by default, `--json` for CI/agents. | yes |
| Human-readable only | No machine-readable output. | |
| JSON only | Machine-readable only. | |

**User's choice:** Human-readable default plus optional JSON.
**Notes:** Local use should stay readable; automation needs a stable structure.

| Option | Description | Selected |
|--------|-------------|----------|
| `error` / `warning` | Simple severity set. | yes |
| `critical` / `warning` / `info` | More GSD-like severity set. | |
| `fail` / `warn` | Short names. | |

**User's choice:** `error` / `warning`.
**Notes:** Severity maps directly to exit-code behavior.

| Option | Description | Selected |
|--------|-------------|----------|
| Fixed fields | Use `severity`, `code`, `path`, `message`, `remediation`. | yes |
| Free-form text | Let each finding print as needed. | |
| Expanded fields | Add line/column/context/source_rule. | |

**User's choice:** Fixed fields.
**Notes:** JSON output should use the same fields.

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit success message | Print `No issues found in .llm-wiki/`. | yes |
| No output | Unix-style quiet success. | |
| Summary table | More verbose success. | |

**User's choice:** Explicit success message.
**Notes:** User prefers clear confirmation that lint actually ran.

---

## the agent's Discretion

- Exact parser function boundaries.
- Finding code names.
- Exact high-confidence secret patterns.
- Repo path detection heuristic details.
- Fixture organization and test names.

## Deferred Ideas

- Future `project-wiki lint --fix`; Phase 3 must not auto-modify files.
- General Markdown link linting.
- Heading-existence validation for `[[page#Heading]]`.
- Semantic repo/wiki contradiction detection.
