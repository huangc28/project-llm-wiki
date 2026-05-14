---
phase: 05
slug: agent-instructions-and-real-repo-validation
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-05-14
---

# Phase 05 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python `unittest` standard library with subprocess and temporary Git repo fixtures |
| **Config file** | none |
| **Quick run command** | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_init.py` |
| **Full suite command** | `python3 -m unittest discover -s skills/project-llm-wiki/tests` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_init.py`.
- **After every plan wave:** Run `python3 -m unittest discover -s skills/project-llm-wiki/tests`.
- **Before `$gsd-verify-work`:** Full suite must be green and `peasydeal_be` dry-run report must show unchanged target repo status.
- **Max feedback latency:** 30 seconds.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 1 | AGENT-01 | T-05-01 | Root `AGENTS.md` gains a short Project LLM Wiki managed section without rewriting unrelated instructions. | unit/subprocess | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_init.py` | No - W0 | pending |
| 05-01-02 | 01 | 1 | AGENT-02, TEST-06 | T-05-02 | NotebookLM, GSD, workflow, and repo-specific text outside Project LLM Wiki markers is byte-for-byte preserved. | unit/subprocess/preservation | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_init.py` | No - W0 | pending |
| 05-01-03 | 01 | 1 | AGENT-03, AGENT-04, AGENT-05 | T-05-03 | Managed section includes the locked index-first, repo-authority, and validated-update-only rules. | unit/subprocess/text | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_init.py` | No - W0 | pending |
| 05-01-04 | 01 | 1 | AGENT-01, AGENT-02 | T-05-04 | Invalid UTF-8, unmatched markers, and duplicate Project LLM Wiki marker pairs do not patch root `AGENTS.md` and produce remediation output. | unit/subprocess/conflict | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_init.py` | No - W0 | pending |
| 05-01-05 | 01 | 1 | AGENT-01 | T-05-05 | `init --dry-run` prints the exact managed section without writing root `AGENTS.md`; `--no-patch-agents` skips AGENTS patching. | unit/subprocess/no-write | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_init.py` | No - W0 | pending |
| 05-02-01 | 02 | 2 | TEST-07 | T-05-06 | `peasydeal_be` validation remains dry-run only and target git status is unchanged before and after. | smoke/report | `python3 skills/project-llm-wiki/scripts/project_wiki.py init --dry-run` from `/Users/huangchihan/develop/bbj/peasydeal/peasydeal_be` | No - report W0 | pending |
| 05-03-01 | 03 | 3 | TEST-07 | T-05-07 | Rollout report gives PASS / FLAG / BLOCK with evidence from package tests and `peasydeal_be` dry-run. | doc/report | `python3 -m unittest discover -s skills/project-llm-wiki/tests` | No - report W0 | pending |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

- [ ] Extend `skills/project-llm-wiki/tests/test_project_wiki_init.py` with root `AGENTS.md` insertion, update, dry-run, `--no-patch-agents`, missing-root-file creation, invalid UTF-8, unmatched marker, duplicate marker, and byte-preservation fixtures.
- [ ] Extend `skills/project-llm-wiki/tests/test_project_wiki_package.py` for `--no-patch-agents`, completed AGENTS integration docs, and Phase 5 testing docs.
- [ ] Create a phase-local rollout report file for `peasydeal_be` dry-run evidence.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Readability of inserted root `AGENTS.md` guidance | AGENT-03, AGENT-04, AGENT-05 | Exact text assertions prove required strings, but a human should confirm the short section is understandable and not overly broad. | Review the managed section printed by `project-wiki init --dry-run` and confirm it clearly states when to read `.llm-wiki/index.md`, repo authority, and validated wiki update rules. |
| Readiness for other PeasyDeal repos | TEST-07 | The PASS / FLAG / BLOCK verdict is a rollout decision, not just a code test. | Review the final rollout report and proceed to `peasydeal_web` / `peasydeal-product-miner` only on PASS or on FLAG with explicit manual acceptance. |

---

## Validation Sign-Off

- [x] All tasks have automated verify commands or Wave 0 dependencies.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify.
- [x] Wave 0 covers all missing references.
- [x] No watch-mode flags.
- [x] Feedback latency < 30 seconds.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** approved 2026-05-14
