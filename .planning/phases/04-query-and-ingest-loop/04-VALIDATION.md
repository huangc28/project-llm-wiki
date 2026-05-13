---
phase: 04
slug: query-and-ingest-loop
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-05-13
---

# Phase 04 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python `unittest` standard library |
| **Config file** | none |
| **Quick run command** | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_query.py` or `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_ingest.py` |
| **Full suite command** | `python3 -m unittest discover -s skills/project-llm-wiki/tests` |
| **Estimated runtime** | ~1 second |

---

## Sampling Rate

- **After every task commit:** Run the targeted query or ingest test file covering the changed behavior.
- **After every plan wave:** Run `python3 -m unittest discover -s skills/project-llm-wiki/tests`.
- **Before `$gsd-verify-work`:** Full suite must be green.
- **Max feedback latency:** 10 seconds.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 1 | QUERY-01 | T-04-01 | Query support reads `.llm-wiki/index.md` before individual pages. | unit/subprocess | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_query.py` | No - W0 | pending |
| 04-01-02 | 01 | 1 | QUERY-02 | T-04-02 | Query protocol requires direct claims to cite repo-local `[[wikilink]]` pages. | unit/doc | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_query.py` | No - W0 | pending |
| 04-01-03 | 01 | 1 | QUERY-03 | T-04-03 | Not-covered responses avoid guessing, list consulted pages, and suggest source types to ingest. | unit/subprocess | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_query.py` | No - W0 | pending |
| 04-01-04 | 01 | 1 | QUERY-04 | T-04-04 | Query log entries store concise summaries, not full transcripts. | unit/subprocess | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_query.py` | No - W0 | pending |
| 04-02-01 | 02 | 2 | INGEST-01 | T-04-05 | Ingest rejects unsafe raw material and keeps raw curated copies policy-gated. | unit/subprocess | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_ingest.py` | No - W0 | pending |
| 04-02-02 | 02 | 2 | INGEST-02 | T-04-06 | Ingest inspects existing pages before creating new durable pages. | unit/subprocess | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_ingest.py` | No - W0 | pending |
| 04-02-03 | 02 | 2 | INGEST-03 | T-04-07 | Summary pages are created only for cross-cutting sources and stay under the blast-radius cap. | unit/subprocess | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_ingest.py` | No - W0 | pending |
| 04-02-04 | 02 | 2 | INGEST-04 | T-04-08 | Touched pages receive provenance; new pages update `index.md`; ingest appends `log.md`. | unit/subprocess | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_ingest.py` | No - W0 | pending |
| 04-02-05 | 02 | 2 | INGEST-05 | T-04-09 | Active task state, checkpoints, full logs, transcripts, secrets, and private data stay out of `.llm-wiki/`. | unit/subprocess | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_ingest.py` | No - W0 | pending |
| 04-03-01 | 03 | 3 | TEST-03 | T-04-10 | Seeded query fixtures prove wikilink-cited output support and query log append behavior without making Python synthesize final answers. | unit/subprocess/protocol | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_query.py` | No - W0 | pending |

---

## Wave 0 Requirements

- [ ] `skills/project-llm-wiki/tests/test_project_wiki_query.py` - fixtures for QUERY-01 through QUERY-04 and TEST-03.
- [ ] `skills/project-llm-wiki/tests/test_project_wiki_ingest.py` - fixtures for INGEST-01 through INGEST-05.
- [ ] `skills/project-llm-wiki/references/testing.md` - Phase 4 targeted command notes.
- [ ] `skills/project-llm-wiki/tests/test_project_wiki_package.py` - update the stdlib import whitelist if Phase 4 adds imports such as `urllib.request` or `urllib.parse`.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Agent-authored final query answer quality | QUERY-02, QUERY-03, TEST-03 | D-07 forbids deterministic Python final-answer generation; tests can verify protocol support and log behavior, but semantic synthesis remains agent-owned. | Review `SKILL.md` query protocol and run a seeded query dry run against fixture pages. Confirm direct claims use `[[wikilink]]` citations and inference is labeled separately. |
| Optional video-source preprocessing | INGEST-01, INGEST-05 | Phase 4 core ingest is adapter-agnostic and must not depend on the user's personal `$watch-video` skill. | Provide curated transcript or summary text as ingest input and confirm raw policy treats it as curated source material, not an authoritative full transcript. |

---

## Validation Sign-Off

- [x] All tasks have automated verify commands or Wave 0 dependencies.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify.
- [x] Wave 0 covers all missing test files.
- [x] No watch-mode flags.
- [x] Feedback latency < 10s.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** approved 2026-05-13
