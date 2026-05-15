---
phase: 05-agent-instructions-and-real-repo-validation
verified: 2026-05-15T07:39:24Z
status: passed
score: 12/12 must-haves verified
overrides_applied: 0
---

# Phase 5: Agent Instructions and Real Repo Validation Verification Report

**Phase Goal:** Add merge-safe repo `AGENTS.md` integration and validate the complete pattern against `peasydeal_be` before broader rollout.
**Verified:** 2026-05-15T07:39:24Z
**Status:** passed
**Re-verification:** No - initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | User can insert a Project LLM Wiki section into root `AGENTS.md` without overwriting unrelated guidance. | VERIFIED | `build_agents_patch_plan()` handles create/append/update/unchanged actions and `run_init()` applies the plan after conflict preflight in `skills/project-llm-wiki/scripts/project_wiki.py:804` and `:1678`. |
| 2 | Existing NotebookLM, GSD, workflow, repo-specific, and CRLF marker-external content is preserved byte-for-byte. | VERIFIED | `test_init_preserves_notebooklm_gsd_and_workflow_sections_byte_for_byte`, `test_init_appends_to_crlf_agents_without_rewriting_existing_bytes`, and `test_init_updates_crlf_marker_section_without_mutating_external_bytes` compare `read_bytes()` / marker-external bytes in `test_project_wiki_init.py:113`, `:169`, and `:202`. |
| 3 | Inserted rules tell agents when to read `.llm-wiki/index.md`, when lookup is not required, that repo code wins, and when wiki updates are allowed. | VERIFIED | Managed section text is rendered in `root_agents_managed_section()` at `project_wiki.py:777` and is visible in live dry-run output; it includes index-first non-trivial lookup, simple typo/narrow edit exemption, repo-code authority, and durable-learning-only updates. |
| 4 | `project-wiki init --dry-run` reports `.llm-wiki/` skeleton effects plus root `AGENTS.md` effects and exact managed section without writing. | VERIFIED | Live dry-run from `peasydeal_be` exited 0, printed would-create paths, `Root AGENTS.md: would append managed section`, and the managed section; no target writes occurred. |
| 5 | `project-wiki init --no-patch-agents` intentionally skips root `AGENTS.md` patching. | VERIFIED | CLI flag exists in `build_parser()` and `test_init_no_patch_agents_skips_root_agents_changes` asserts original `AGENTS.md` bytes are unchanged while `.llm-wiki/index.md` is created. |
| 6 | Invalid UTF-8, unmatched markers, and duplicate marker conflicts stop without partial writes. | VERIFIED | `build_agents_patch_plan()` returns conflict actions for unreadable UTF-8 and marker conflicts before `apply_init_plan()`; tests assert return code 2, unchanged `AGENTS.md` bytes, and absent `.llm-wiki/` for all required cases. |
| 7 | `peasydeal_be` validation is dry-run-only and leaves target status unchanged with no target `.llm-wiki/`. | VERIFIED | Live checks: target git root resolved to `/Users/huangchihan/develop/bbj/peasydeal/peasydeal_be`; pre/post `git status --short` were empty; `test ! -d .../.llm-wiki` passed after dry-run. |
| 8 | Rollout report uses a matching `PASS` / `FLAG` / `BLOCK` verdict and currently reports `PASS`. | VERIFIED | `05-ROLLOUT-REPORT.md:6` has `verdict: PASS`; `:11` has `Verdict: PASS`; Python frontmatter/body consistency check exited 0. |
| 9 | Rollout report states whether to proceed to `peasydeal_web` and `peasydeal-product-miner`. | VERIFIED | `05-ROLLOUT-REPORT.md:19` defines next-repo application rules and `:21` names `peasydeal_web, peasydeal-product-miner`. |
| 10 | Skill and reference docs document default AGENTS patching, dry-run preview, no-patch opt-out, conflicts, and Phase 5 validation. | VERIFIED | `SKILL.md:31`, `command-surface.md:23`, and `testing.md:112` document the implemented contract; package tests assert these docs. |
| 11 | All Phase 5 requirement IDs are claimed by at least one plan and mapped in `REQUIREMENTS.md`. | VERIFIED | Plans cover AGENT-01 through AGENT-05, TEST-06, and TEST-07; `REQUIREMENTS.md` maps all seven to Phase 5 with no orphaned Phase 5 IDs. |
| 12 | Full package suite currently passes. | VERIFIED | `env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests` passed: 143 tests in 22.697s. |

**Score:** 12/12 truths verified

### Plan Must-Have Coverage

| Must-Have Group | Status | Evidence |
|---|---|---|
| D-01, D-02, D-12, D-13, D-16 | VERIFIED | Root `AGENTS.md` constants, create/append/update/unchanged planning, exact markers, and marker-bounded replacement exist in `project_wiki.py:14`, `:777`, `:804`, and `:850`. |
| D-03, D-15 | VERIFIED | Invalid UTF-8, unmatched start/end markers, and duplicate marker pairs return conflicts in `project_wiki.py:839`, `:863`, `:867`, and `:871`; tests assert no writes. |
| D-04 | VERIFIED | Dry-run prints skeleton paths, source status, root `AGENTS.md` action, and managed section via `run_init()` / `print_agents_patch_plan()` at `project_wiki.py:1682` and `:893`. |
| D-05 | VERIFIED | `--no-patch-agents` maps to `patch_agents=False` at `project_wiki.py:1678` and is tested in `test_project_wiki_init.py:261`. |
| D-06 through D-11 | VERIFIED | Managed section is short and protocol-oriented; it contains non-trivial lookup, simple-edit exemption, relevant-pages-only lookup, durable update boundary, task-state exclusion, and repo-code authority. |
| D-14, TEST-06 | VERIFIED | Byte-preservation tests cover NotebookLM/GSD/workflow sections and CRLF append/update cases using `read_bytes()` and marker-external byte comparison. |
| D-17 | VERIFIED | Init fixture suite covers creation, append, update, dry-run no-write, opt-out, marker conflicts, invalid UTF-8, and preservation behavior. |
| D-18, D-19, TEST-07 | VERIFIED | Live `peasydeal_be` dry-run and `05-ROLLOUT-REPORT.md` record target root, command, would-create paths, managed section, conflict status, before/after status, and no `.llm-wiki/`. |
| D-20 | VERIFIED | Rollout report verdict is `PASS`, body/frontmatter match, and next-repo rules name `peasydeal_web` and `peasydeal-product-miner`. |

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `skills/project-llm-wiki/scripts/project_wiki.py` | Root AGENTS patch planning, dry-run rendering, conflict detection, and `--no-patch-agents`. | VERIFIED | `gsd-sdk query verify.artifacts` passed; manual checks confirm substantive implementation and runtime wiring. |
| `skills/project-llm-wiki/tests/test_project_wiki_init.py` | Subprocess fixtures for insertion, update, dry-run, no-write, conflict, and byte preservation. | VERIFIED | Targeted suite passed: 25 tests. |
| `skills/project-llm-wiki/tests/test_project_wiki_package.py` | Help/docs assertions for Phase 5 command surface and validation contract. | VERIFIED | Package-doc suite passed: 20 tests. |
| `skills/project-llm-wiki/SKILL.md` | Skill-level default root AGENTS patching and lookup protocol. | VERIFIED | Documents default patching, dry-run preview, no-patch opt-out, and index-first lookup. |
| `skills/project-llm-wiki/references/command-surface.md` | User-facing command contract for `init`, `--dry-run`, and `--no-patch-agents`. | VERIFIED | Package tests assert completed contract and absence of old deferred Phase 5 entry. |
| `skills/project-llm-wiki/references/testing.md` | Phase 5 validation contract. | VERIFIED | Covers AGENT-01 through AGENT-05, TEST-06, TEST-07, dry-run-only target gate, and PASS/FLAG/BLOCK semantics. |
| `.planning/phases/05-agent-instructions-and-real-repo-validation/05-ROLLOUT-REPORT.md` | Dry-run evidence, package test evidence, PASS verdict, and next-repo rules. | VERIFIED | Frontmatter/body verdict match; live target checks confirmed no write. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `project_wiki.py` | root `AGENTS.md` | `run_init()` builds one AGENTS plan for dry-run/apply | WIRED | `agents_plan = build_agents_patch_plan(...)` is created before dry-run/apply branching in `project_wiki.py:1678`. |
| `project_wiki.py` | `apply_init_plan()` | Combined skeleton and AGENTS conflicts checked before writes | WIRED | SDK literal pattern check missed this, but code builds `all_conflicts = [*conflicts, *agents_conflicts]` and returns before `apply_init_plan()` at `project_wiki.py:1703` and `:1717`. |
| `test_project_wiki_init.py` | root AGENTS byte preservation | `read_bytes()` and marker-external byte comparison | WIRED | Byte tests cover markerless CRLF append, CRLF marker update, and NotebookLM/GSD/workflow preservation. |
| `05-ROLLOUT-REPORT.md` | `peasydeal_be` validation | Dry-run command and target working directory recorded | WIRED | Report records command at line 41 and working directory at line 43; live rerun matched. |
| `test_project_wiki_package.py` | command/testing docs | Package assertions lock docs | WIRED | Tests at `test_project_wiki_package.py:160` and `:211` assert command-surface and Phase 5 validation docs. |
| `05-ROLLOUT-REPORT.md` | next PeasyDeal repos | Next-repo checklist | WIRED | Report names both next targets and dry-run-first rules. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|---|---|---|---|---|
| `project_wiki.py` | `agents_plan` | `build_agents_patch_plan(git_root, patch_agents=not args.no_patch_agents)` reads actual root `AGENTS.md` bytes and markers. | Yes | FLOWING |
| `project_wiki.py` | `content_bytes` | Managed section plus existing file bytes; `apply_agents_patch_plan()` writes bytes only for create/append/update. | Yes | FLOWING |
| `05-ROLLOUT-REPORT.md` | rollout verdict and evidence | Live dry-run/status/test evidence plus documented report checks. | Yes | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Target repo root is correct | `git -C /Users/huangchihan/develop/bbj/peasydeal/peasydeal_be rev-parse --show-toplevel` | `/Users/huangchihan/develop/bbj/peasydeal/peasydeal_be` | PASS |
| Target status before dry-run | `git -C /Users/huangchihan/develop/bbj/peasydeal/peasydeal_be status --short` | empty | PASS |
| Real target dry-run | `env PYTHONDONTWRITEBYTECODE=1 python3 .../project_wiki.py init --dry-run` from `peasydeal_be` | exit 0; would-create paths and managed `AGENTS.md` section printed | PASS |
| Target status after dry-run | `git -C /Users/huangchihan/develop/bbj/peasydeal/peasydeal_be status --short` | empty | PASS |
| Target `.llm-wiki/` absent | `test ! -d /Users/huangchihan/develop/bbj/peasydeal/peasydeal_be/.llm-wiki` | exit 0 | PASS |
| Init/AGENTS suite | `env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_init.py` | Ran 25 tests; OK | PASS |
| Package docs/help suite | `env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_package.py` | Ran 20 tests; OK | PASS |
| Full package suite | `env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests` | Ran 143 tests; OK | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| AGENT-01 | 05-01, 05-03 | Add Project LLM Wiki section to repo `AGENTS.md` without overwriting unrelated instructions. | SATISFIED | Implementation preserves existing bytes; tests cover append/update/create. |
| AGENT-02 | 05-01, 05-03 | Preserve NotebookLM sections and workflow-specific guidance. | SATISFIED | Preservation fixture covers NotebookLM, GSD, and repo-specific workflow sections byte-for-byte. |
| AGENT-03 | 05-01, 05-03 | Rules tell agents to read `.llm-wiki/index.md` before non-trivial work. | SATISFIED | Managed section and docs contain this exact protocol; live dry-run printed it. |
| AGENT-04 | 05-01, 05-03 | Rules state current repo code is authoritative over `.llm-wiki/`. | SATISFIED | Managed section says current repository files are authoritative when they disagree with `.llm-wiki/`. |
| AGENT-05 | 05-01, 05-03 | Rules tell agents to update `.llm-wiki/` only after validated durable learning and never use it for task status. | SATISFIED | Managed section includes validated durable-learning update rule and active task status exclusion. |
| TEST-06 | 05-01 | Fixture preserves NotebookLM section. | SATISFIED | `test_init_preserves_notebooklm_gsd_and_workflow_sections_byte_for_byte` passes in the targeted suite. |
| TEST-07 | 05-02, 05-03 | Pattern dry-run validated against `peasydeal_be` before other PeasyDeal repos. | SATISFIED | Live dry-run from target repo passed with unchanged target status and absent target `.llm-wiki/`; report names next repos under dry-run-first rules. |

No orphaned Phase 5 requirements were found in `REQUIREMENTS.md`; all seven declared Phase 5 IDs appear in plan frontmatter.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `skills/project-llm-wiki/scripts/project_wiki.py` | 122 | `PLACEHOLDER_SECRET_VALUES` | INFO | False positive from secret-detection allowlist, not a stub. |
| `skills/project-llm-wiki/scripts/project_wiki.py` | multiple | Empty list initializers | INFO | Normal accumulator initialization; not hardcoded rendered output or disconnected data. |

No TODO/FIXME/placeholder implementation, no console-only handler, and no hardcoded empty user-visible data source was found in Phase 5 files.

### Human Verification Required

None.

### Gaps Summary

No gaps found. All roadmap success criteria, Phase 5 plan must-haves, required artifacts, key links, requirement IDs, dry-run target checks, and package tests are verified.

---

_Verified: 2026-05-15T07:39:24Z_
_Verifier: the agent (gsd-verifier)_
