---
phase: 02-init-and-wiki-templates
verified: 2026-05-13T00:10:12Z
status: passed
score: "16/16 must-haves verified"
overrides_applied: 0
---

# Phase 2: Init and Wiki Templates Verification Report

**Phase Goal:** Implement safe `.llm-wiki/` initialization with idempotent templates and raw source policy.
**Verified:** 2026-05-13T00:10:12Z
**Status:** passed
**Re-verification:** No - initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | User can run init in a clean git repo and see `.llm-wiki/` files in `git status`. | VERIFIED | `test_clean_repo_status_shows_llm_wiki_files` runs init in a temp Git repo, runs `git status --short`, and asserts `.llm-wiki/` visibility plus required files (`test_project_wiki_init.py:245-265`). Fresh full suite passed 22 tests. |
| 2 | User can rerun init without duplicated sections or overwritten notes. | VERIFIED | Existing `index.md` and `repo-overview.md` are sentinel-edited, init reruns, sentinels remain, and missing index links are reported (`test_project_wiki_init.py:267-290`). Implementation writes through `create_file_if_missing` and skips existing paths (`project_wiki.py:217-245`). |
| 3 | User can read seeded wiki templates that define durable project knowledge, raw source policy, and repo-code authority. | VERIFIED | Templates state repo code authority (`llm-wiki/README.md:7`, `llm-wiki/AGENTS.md:5`), durable/non-active-state boundaries (`README.md:9-21`, `log.md:3-5`), and raw policy (`raw/README.md:5-19`). |
| 4 | User receives clear output identifying the git root used for initialization. | VERIFIED | `run_init` prints `Resolved git root:` after `resolve_git_root` succeeds (`project_wiki.py:273-286`); dry-run spot-check printed the current repo root. |
| 5 | Init handles missing common seed files gracefully. | VERIFIED | `build_repo_overview` checks only `README.md` and `AGENTS.md`, records found/skipped sources, and never blocks skeleton creation (`project_wiki.py:117-139`, `268-270`); dry-run without `AGENTS.md` is covered at `test_project_wiki_init.py:102-116`. |
| 6 | INIT-01: `.llm-wiki/` initializes in the actual Git root detected by `git rev-parse --show-toplevel`. | VERIFIED | `resolve_git_root` calls `subprocess.run(["git", "rev-parse", "--show-toplevel"], ...)` (`project_wiki.py:62-73`); nested cwd test asserts files are created at repo root, not nested cwd (`test_project_wiki_init.py:52-83`). |
| 7 | INIT-02: non-git or multi-repo parent runs fail clearly without writing. | VERIFIED | Non-git path returns 2 and prints `No git repository found...`; child repo candidates are listed for parent workspaces (`project_wiki.py:273-284`); tests assert no parent `.llm-wiki/` is created (`test_project_wiki_init.py:85-100`). |
| 8 | INIT-03: missing skeleton creates required files and directories. | VERIFIED | Required directories/files include README, AGENTS, index, log, raw policy, raw curated, architecture/domain/decisions/operations/features/summaries, ideas, repo-overview, and `.gitkeep` files (`project_wiki.py:10-40`); temp repo test asserts created files (`test_project_wiki_init.py:65-80`). |
| 9 | INIT-04: rerun does not overwrite existing wiki notes or duplicate generated sections. | VERIFIED | Existing files are skipped before writes (`project_wiki.py:217-245`), and rerun test proves sentinel preservation plus skipped-path output (`test_project_wiki_init.py:267-290`). |
| 10 | INIT-05: concise starting page seeding is implemented and source-scoped. | VERIFIED | `repo-overview.md` is generated with provenance lines for README/AGENTS only (`project_wiki.py:117-139`, `142-152`). The plan/context intentionally excludes package manifests; tests assert `package.json`, `pyproject.toml`, `go.mod`, and `Cargo.toml` do not appear in seeded output (`test_project_wiki_init.py:292-313`). |
| 11 | INIT-06: `.llm-wiki/` appears in `git status` after clean init unless ignored. | VERIFIED | `test_clean_repo_status_shows_llm_wiki_files` runs `git status --short` and asserts `.llm-wiki/` output (`test_project_wiki_init.py:245-259`). |
| 12 | RAW-01: raw README explains allowed and disallowed raw sources. | VERIFIED | `raw/README.md` contains `Allowed`, `Denied`, and `Before Adding Raw Material` sections (`raw/README.md:5-19`). |
| 13 | RAW-02: unsafe material is explicitly forbidden. | VERIFIED | Denied phrase includes secrets, credentials, auth tokens, private customer data, full logs, database exports, and generated dumps in raw policy and agent/template text (`raw/README.md:13`, `raw/curated/README.md:9`, `AGENTS.md:11`). |
| 14 | RAW-03: curated raw sources are limited to de-secreted, intentionally selected, small excerpts. | VERIFIED | `raw/curated/README.md:3-7` requires de-secreted, intentionally selected, small sources or excerpts and gives example filename `2026-05-13-api-notes.md`. |
| 15 | TEST-01: clean test repo can run init and show `.llm-wiki/` in Git status. | VERIFIED | Temporary Git repo fixture initializes a repo, runs helper subprocess, then asserts `git status --short` includes `.llm-wiki/` (`test_project_wiki_init.py:23-50`, `245-259`). |
| 16 | TEST-02: clean test repo can rerun init without duplication or overwrite. | VERIFIED | Rerun fixture edits generated files, reruns init, and asserts sentinel content remains while recommended links are reported (`test_project_wiki_init.py:267-290`). |

**Score:** 16/16 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `skills/project-llm-wiki/scripts/project_wiki.py` | Safe init implementation | VERIFIED | Contains Git root resolver, no `--target`, `--dry-run`, preflight conflicts, template loading, README/AGENTS-only overview generation, missing-only file writes, and output sections (`project_wiki.py:62-365`). |
| `skills/project-llm-wiki/tests/test_project_wiki_init.py` | Integration validation for Phase 2 | VERIFIED | 15 init tests cover Git root, parent refusal, dry-run, conflicts, symlinks, invalid index, git status, idempotency, seed-source exclusions, raw policy, and ideas content (`test_project_wiki_init.py:52-347`). |
| `skills/project-llm-wiki/tests/test_project_wiki_package.py` | Package/helper validation | VERIFIED | Covers help/version, non-git refusal, stdlib import whitelist, and template inventory (`test_project_wiki_package.py:39-88`). |
| `skills/project-llm-wiki/assets/templates/llm-wiki/README.md` | Wiki purpose and boundaries | VERIFIED | Includes purpose, belongs/does-not-belong sections, example links, and repo-code authority (`README.md:1-27`). |
| `skills/project-llm-wiki/assets/templates/llm-wiki/AGENTS.md` | Agent-facing wiki usage rules | VERIFIED | Tells agents to read index, trust repo files over wiki notes, avoid task status, and avoid unsafe material (`AGENTS.md:1-11`). |
| `skills/project-llm-wiki/assets/templates/llm-wiki/index.md` | Default navigation | VERIFIED | Links `[[summaries/repo-overview]]` and `[[features/ideas]]`, and names architecture/domain/decisions/operations/features/summaries/raw sources (`index.md:1-34`). |
| `skills/project-llm-wiki/assets/templates/llm-wiki/log.md` | Durable wiki log guidance | VERIFIED | Includes `# Project LLM Wiki Log`, active-state boundary, and `## Entries` (`log.md:1-9`). |
| `skills/project-llm-wiki/assets/templates/llm-wiki/raw/README.md` | Strict raw source policy | VERIFIED | Contains allowed, denied, and pre-add checks with the required unsafe-material list (`raw/README.md:1-20`). |
| `skills/project-llm-wiki/assets/templates/llm-wiki/raw/curated/README.md` | Curated raw source rules | VERIFIED | Requires de-secreted, intentionally selected, small sources/excerpts and the example filename (`raw/curated/README.md:1-9`). |
| `skills/project-llm-wiki/assets/templates/llm-wiki/features/ideas.md` | Durable ideas page | VERIFIED | Includes Thought, Why it might matter, Current leaning, Not decided, Related links, and non-roadmap/task-state warning (`features/ideas.md:1-25`). |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `project_wiki.py` | Git CLI | `subprocess.run` argument list | WIRED | `resolve_git_root` calls `git rev-parse --show-toplevel` with an argument list and `check=False` (`project_wiki.py:62-73`). |
| `project_wiki.py` | `.llm-wiki` path plan | path constants rooted at resolved Git root | WIRED | Required relative paths are constants (`project_wiki.py:10-54`), and `run_init` applies them under `git_root` after resolving root (`project_wiki.py:273-325`). |
| `project_wiki.py` | template assets | `template_root` and `load_template_contents` | WIRED | Template root resolves to `assets/templates/llm-wiki`; each template maps from target `.llm-wiki` path to package asset path (`project_wiki.py:93-110`). |
| `project_wiki.py` | `.llm-wiki/summaries/repo-overview.md` | `build_repo_overview` and file-content map | WIRED | Overview is generated from README/AGENTS source status and inserted into init contents (`project_wiki.py:117-152`). |
| `test_project_wiki_init.py` | `project_wiki.py` | subprocess helper execution | WIRED | `HELPER` points at `scripts/project_wiki.py`; tests invoke it with current cwd (`test_project_wiki_init.py:8-10`, `34-41`). |
| `test_project_wiki_init.py` | Git status visibility | `git status --short` | WIRED | `git_status_short` runs `git status --short`; clean repo test asserts `.llm-wiki/` appears (`test_project_wiki_init.py:43-50`, `245-259`). |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `project_wiki.py` | `git_root` | `git rev-parse --show-toplevel` stdout | Yes | FLOWING - `run_init` refuses when absent and uses resolved root for all path planning (`project_wiki.py:62-73`, `273-286`). |
| `project_wiki.py` | `file_contents` | static templates plus generated repo overview and `.gitkeep` entries | Yes | FLOWING - template text is read from package assets, generated overview is added, and apply writes missing files only (`project_wiki.py:97-152`, `217-247`). |
| `project_wiki.py` | `found_sources` / `skipped_sources` | target repo `README.md` and `AGENTS.md` existence | Yes | FLOWING - source status appears in output and generated overview (`project_wiki.py:117-139`, `268-270`). |
| `test_project_wiki_init.py` | helper subprocess output and target repo files | temporary Git repositories | Yes | FLOWING - tests create real temp repos, run the CLI, inspect files, and run Git status (`test_project_wiki_init.py:23-50`, `52-347`). |
| Markdown templates | policy/navigation text | static package assets | Yes | STATIC BY DESIGN - templates are copied as durable starter content and validated by content tests. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full package suite | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests` | Exit 0; 22 tests ran OK in 1.700s. | PASS |
| Init help exposes dry-run | `python3 skills/project-llm-wiki/scripts/project_wiki.py init --help` | Exit 0; usage includes `--dry-run`. | PASS |
| `--target` remains unsupported | `python3 skills/project-llm-wiki/scripts/project_wiki.py init --target /tmp` | Exit 2; argparse reports `unrecognized arguments: --target /tmp`. | PASS |
| Dry-run reports root without writing | `python3 skills/project-llm-wiki/scripts/project_wiki.py init --dry-run` | Exit 0; printed resolved git root, would-create paths, source status, and next step. | PASS |
| Schema drift gate | `gsd-sdk query verify.schema-drift 02` | `drift_detected: false`, `blocking: false`. | PASS |
| Codebase drift gate | `gsd-sdk query verify.codebase-drift` | Skipped non-blocking with reason `no-structure-md`. | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| INIT-01 | `02-01-PLAN.md`, `02-03-PLAN.md` | Initialize `.llm-wiki/` in actual Git root detected by `git rev-parse --show-toplevel`. | SATISFIED | Resolver uses exact Git command (`project_wiki.py:62-73`); nested temp repo test proves root placement (`test_project_wiki_init.py:52-83`). |
| INIT-02 | `02-01-PLAN.md`, `02-03-PLAN.md` | Clear failure or target-selection message outside intended repo. | SATISFIED | Non-git return path prints failure, candidate repos, and cd instruction with no writes (`project_wiki.py:273-284`; tests `85-100`). |
| INIT-03 | `02-02-PLAN.md`, `02-03-PLAN.md` | Create required `.llm-wiki/` skeleton. | SATISFIED | Required directories/files are enumerated in code and asserted in clean-init tests (`project_wiki.py:10-40`; `test_project_wiki_init.py:65-80`). |
| INIT-04 | `02-01-PLAN.md`, `02-03-PLAN.md` | Rerun without overwriting or duplication. | SATISFIED | Missing-only writes and sentinel rerun test (`project_wiki.py:217-245`; `test_project_wiki_init.py:267-290`). |
| INIT-05 | `02-02-PLAN.md`, `02-03-PLAN.md` | Seed concise starting pages from existing repo files. | SATISFIED | `repo-overview.md` records README/AGENTS source status; locked context intentionally excludes manifests to avoid stale tech-stack facts, and tests assert that exclusion (`project_wiki.py:117-139`; `test_project_wiki_init.py:292-313`). |
| INIT-06 | `02-03-PLAN.md` | Show `.llm-wiki/` files in Git status after init unless ignored. | SATISFIED | Test runs `git status --short` and asserts `.llm-wiki/` output (`test_project_wiki_init.py:245-259`). |
| RAW-01 | `02-02-PLAN.md`, `02-03-PLAN.md` | Explain allowed and disallowed raw sources. | SATISFIED | `raw/README.md` has allowed, denied, and before-add sections (`raw/README.md:5-19`). |
| RAW-02 | `02-02-PLAN.md`, `02-03-PLAN.md` | Warn not to store unsafe material. | SATISFIED | Required denied list appears in raw and curated policy templates (`raw/README.md:13`; `raw/curated/README.md:9`). |
| RAW-03 | `02-02-PLAN.md`, `02-03-PLAN.md` | Only curated, de-secreted project sources under raw curated. | SATISFIED | Curated README requires de-secreted, intentionally selected, small sources/excerpts (`raw/curated/README.md:3-7`). |
| TEST-01 | `02-03-PLAN.md` | Clean test repo can run init and show `.llm-wiki/` in Git status. | SATISFIED | Temp repo Git status fixture passes in full suite (`test_project_wiki_init.py:245-259`; suite 22 tests OK). |
| TEST-02 | `02-03-PLAN.md` | Clean test repo can rerun init without duplicated sections or overwritten notes. | SATISFIED | Sentinel rerun fixture passes in full suite (`test_project_wiki_init.py:267-290`; suite 22 tests OK). |

No orphaned Phase 2 requirements found. `.planning/ROADMAP.md` maps Phase 2 to INIT-01 through INIT-06, RAW-01 through RAW-03, TEST-01, and TEST-02; all are present in plan frontmatter and accounted for above. Note: `.planning/REQUIREMENTS.md` still marks INIT-06, TEST-01, and TEST-02 as pending in metadata, but implementation and tests satisfy them.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `skills/project-llm-wiki/scripts/project_wiki.py` | 195, 200 | `return [], None` / `return [], "...could not read"` | INFO | Intentional tuple return for index-link inspection; not a stub and covered by invalid-index tests. |

No TODO/FIXME/HACK markers, placeholders, `shell=True`, console-log-only handlers, hardcoded empty user-visible data, or orphaned Phase 2 artifacts were found. The SDK artifact/key-link checks had literal-pattern false negatives for split Python tokens; manual line-level verification above confirms the links are wired.

### Human Verification Required

None. Phase 2 is a deterministic CLI/template/test phase. Visual, real-time, external-service, and performance-feel checks are not applicable.

### Gaps Summary

No blocking gaps found. Phase 2 achieves the roadmap goal: init is Git-rooted, safe, idempotent, dry-run capable, conflict-preflighted, template-backed, raw-policy aware, and covered by temporary Git repository regression tests.

---

_Verified: 2026-05-13T00:10:12Z_
_Verifier: the agent (gsd-verifier)_
