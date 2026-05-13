---
phase: 03
slug: lint-and-safety-checks
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-13
---

# Phase 03 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python `unittest` with standard-library subprocess and temporary Git repo fixtures |
| **Config file** | none |
| **Quick run command** | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_lint.py` |
| **Full suite command** | `python3 -m unittest discover -s skills/project-llm-wiki/tests` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After Plan 03-01 tasks:** Run targeted lint tests for wikilinks, missing index entries, and raw file size warnings.
- **After Plan 03-02 tasks:** Run targeted lint tests for secret-looking content, stale `updated:` frontmatter, repo path drift warnings, and warning-only exit behavior.
- **After Plan 03-03 tasks:** Run `python3 -m unittest discover -s skills/project-llm-wiki/tests`; the full Phase 3 suite must be green.
- **Before `$gsd-verify-work`:** Full suite must be green.
- **Max feedback latency:** 30 seconds.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | LINT-01 | T-03-01 | Broken Obsidian wikilinks produce `error` findings, `../` wikilinks cannot escape `.llm-wiki/`, and failures exit 1 | integration | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_lint.py` | creates W0 | pending |
| 03-01-02 | 01 | 1 | LINT-02, TEST-04 | T-03-02 | Missing main wiki pages in `.llm-wiki/index.md`, including `raw/curated/README.md`, produce warning-only findings while other raw curated sources are excluded | integration | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_lint.py` | creates W0 | pending |
| 03-01-03 | 01 | 1 | LINT-04 | T-03-03 | Oversized files under `.llm-wiki/raw/` produce warning-only findings without reading unrelated repo files | integration | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_lint.py` | creates W0 | pending |
| 03-02-01 | 02 | 2 | LINT-03, TEST-05 | T-03-04 | High-confidence secret-looking content in all wiki files, including non-`.md` raw files, produces warning-only findings with redaction-oriented remediation and symlink escapes are not followed | integration/safety | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_lint.py` | yes - after W0 | pending |
| 03-02-02 | 02 | 2 | LINT-05 | T-03-05 | Only top frontmatter `updated:` dates older than 90 days produce stale warnings | integration | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_lint.py` | yes - after W0 | pending |
| 03-02-03 | 02 | 2 | LINT-06 | T-03-06 | Repo path drift warnings inspect only inline code spans and fenced code blocks, ignore outside-repo candidates, and ignore ordinary prose paths | integration | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_lint.py` | yes - after W0 | pending |
| 03-02-04 | 02 | 2 | LINT-03, LINT-04, LINT-05, LINT-06 | T-03-07 | Warning-only lint runs exit 0 so CI can report non-blocking safety debt | integration | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_lint.py` | yes - after W0 | pending |
| 03-03-01 | 03 | 3 | LINT-07 | T-03-08 | Text and JSON renderers expose exactly `severity`, `code`, `path`, `message`, and `remediation` for every finding | integration/output | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_lint.py` | yes - after W0 | pending |
| 03-03-02 | 03 | 3 | TEST-04 | T-03-02 | Fixture with an intentionally removed index wikilink reports `missing_index_entry` | integration | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_lint.py` | yes - after W0 | pending |
| 03-03-03 | 03 | 3 | TEST-05 | T-03-04 | Fixture with intentionally secret-looking raw content reports `secret_like_content` | integration/safety | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_lint.py` | yes - after W0 | pending |
| 03-03-04 | 03 | 3 | LINT-01, LINT-07 | T-03-09 | Clean initialized wiki prints `No issues found in .llm-wiki/` and JSON output remains parseable | integration/output | `python3 -m unittest discover -s skills/project-llm-wiki/tests` | yes - after W0 | pending |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

Scheduled by Phase 3 plans before production lint implementation is considered complete.

- [ ] `skills/project-llm-wiki/tests/test_project_wiki_lint.py` with temporary Git repo fixtures that run `project-wiki init` and `project-wiki lint`.
- [ ] RED tests for broken wikilinks, `../` wikilink escapes, symlink/outside-root file collection, missing index coverage including `raw/curated/README.md`, oversized raw files, non-`.md` secret-looking raw content, stale `updated:` frontmatter, repo path drift, outside-repo path candidates, ordinary prose paths, text output, JSON output, success output, and exit-code behavior.
- [ ] `skills/project-llm-wiki/tests/test_project_wiki_package.py` import whitelist updated only for Python standard-library imports used by lint, such as `datetime`, `json`, and `re`.
- [ ] Test helpers assert that lint is read-only by comparing wiki file contents before and after warning-producing runs.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| None | N/A | Phase 3 behavior is deterministic and should be covered by automated subprocess fixtures | N/A |

---

## Validation Sign-Off

- [ ] All tasks have automated verify commands or Wave 0 dependencies.
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify.
- [ ] Wave 0 covers all currently missing references.
- [ ] No watch-mode flags.
- [ ] Feedback latency < 30 seconds.
- [ ] `nyquist_compliant: true` set in frontmatter after Wave 0 tests exist and pass.

**Approval:** pending
