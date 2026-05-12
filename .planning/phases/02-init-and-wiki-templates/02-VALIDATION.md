---
phase: 02
slug: init-and-wiki-templates
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-13
---

# Phase 02 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python `unittest` with standard-library subprocess and temporary Git repo fixtures |
| **Config file** | none |
| **Quick run command** | `python3 -m unittest discover -s skills/project-llm-wiki/tests` |
| **Full suite command** | `python3 -m unittest discover -s skills/project-llm-wiki/tests` |
| **Estimated runtime** | ~1 second |

---

## Sampling Rate

- **After Wave 1 / Plan 02-03 tasks:** Run the RED gate wrapper from `02-03-PLAN.md`; it exits 0 only while the new Phase 2 tests exist and fail before implementation.
- **After Wave 2 / Plan 02-01 tasks:** Run targeted package tests plus the wrapped negative `--target` verifier from `02-01-PLAN.md`; template and seed-content RED tests remain owned by Plan 02-02.
- **After Wave 3 / Plan 02-02 tasks:** Run `python3 -m unittest discover -s skills/project-llm-wiki/tests`; the full Phase 2 suite must be green.
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 02-03-01 | 03 | 1 | TEST-01, INIT-01, INIT-02, INIT-04 | T-02-02, T-02-03 | RED tests for clean repo init, subdirectory root targeting, parent refusal, dry-run, and conflicts | integration | `python3 -c 'import subprocess, sys; result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "skills/project-llm-wiki/tests"]); sys.exit(0 if result.returncode != 0 else 1)'` | creates W0 | pending |
| 02-03-02 | 03 | 1 | TEST-02, INIT-03, INIT-05, INIT-06, RAW-01, RAW-02, RAW-03 | T-02-01, T-02-03 | RED tests for idempotency, git status, seed-source limits, raw policy, and ideas content | integration/content | `python3 -c 'import subprocess, sys; result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "skills/project-llm-wiki/tests"]); sys.exit(0 if result.returncode != 0 else 1)'` | creates W0 | pending |
| 02-01-01 | 01 | 2 | INIT-01 | T-02-02 | Writes only under `git rev-parse --show-toplevel` | integration | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_package.py` | yes - after 02-03 | pending |
| 02-01-02 | 01 | 2 | INIT-02 | T-02-02 | Refuses non-git and parent workspace contexts without writes | integration | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_package.py` | yes - after 02-03 | pending |
| 02-01-03 | 01 | 2 | INIT-04 | T-02-03 | Preflights conflicts before any partial writes and never overwrites existing wiki files | integration | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_package.py` | yes - after 02-03 | pending |
| 02-01-04 | 01 | 2 | INIT-04 | T-02-03 | `--dry-run` reports would-create, would-skip, and conflicts without writing | integration | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_package.py` | yes - after 02-03 | pending |
| 02-02-01 | 02 | 3 | INIT-03 | T-02-01 | Creates required skeleton files/directories and `.gitkeep` placeholders only when missing | integration/content | `python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_package.py` | yes - after 02-03 | pending |
| 02-02-02 | 02 | 3 | INIT-05 | T-02-01 | Seeds only from `README.md` and `AGENTS.md`, with provenance and skipped-source reporting | integration/content | `python3 -m unittest discover -s skills/project-llm-wiki/tests` | yes - after 02-03 | pending |
| 02-02-03 | 02 | 3 | RAW-01, RAW-02, RAW-03 | T-02-01 | Raw policy templates forbid secrets and limit curated raw sources to de-secreted excerpts | content | `python3 -m unittest discover -s skills/project-llm-wiki/tests` | yes - after 02-03 | pending |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

Scheduled by `02-03-PLAN.md` in wave 1 before implementation plans. It is a TDD/RED plan: verification succeeds when the tests are present and the suite fails before production implementation. Plans `02-01` and `02-02` own the GREEN transition.

- [ ] `skills/project-llm-wiki/tests/test_project_wiki_init.py` or equivalent test methods for clean Git repo init, subdirectory root detection, parent workspace refusal, dry-run, conflicts, idempotency, and `git status --short` visibility.
- [ ] Existing import whitelist in `skills/project-llm-wiki/tests/test_project_wiki_package.py` updated for any new standard-library imports such as `subprocess`, `tempfile`, `dataclasses`, or `shutil`.
- [ ] Temporary Git repo fixture helper using `tempfile.TemporaryDirectory` and `git init`.
- [ ] Content assertions for `.llm-wiki/raw/README.md`, `.llm-wiki/raw/curated/README.md`, `.llm-wiki/features/ideas.md`, and `.llm-wiki/summaries/repo-overview.md`.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| None | N/A | All Phase 2 behaviors should be covered by automated unit or integration tests | N/A |

---

## Validation Sign-Off

- [ ] All tasks have automated verify commands or Wave 0 dependencies.
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify.
- [ ] Wave 0 covers all currently missing references.
- [ ] No watch-mode flags.
- [ ] Feedback latency < 30 seconds.
- [ ] `nyquist_compliant: true` set in frontmatter after Wave 0 tests exist and pass.

**Approval:** pending
