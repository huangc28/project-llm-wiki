# Phase 1 Research: Skill Package Foundation

**Phase:** 1 - Skill Package Foundation
**Researched:** 2026-05-12
**Status:** Complete

## Research Question

What do we need to know to plan the reusable Project LLM Wiki skill package foundation well?

## Phase Boundary

Phase 1 should establish the reusable package surface, not implement full init/lint/query/ingest behavior. The phase should leave later phases with a clear package directory, command surface, file ownership model, no-dependency script entrypoint, and baseline tests that prove the package is inspectable and runnable.

## Inputs Read

- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/research/SUMMARY.md`
- `AGENTS.md`

## Key Findings

### 1. Package Location Should Be Repo-Local First

The project already exists as a dedicated git repo for the Project LLM Wiki skill. Phase 1 should make this repo the working source of truth for the reusable package, while documenting that installation may later mirror or symlink into vault-managed skills or `~/.codex/skills`.

Planning implication:
- Create `skills/project-llm-wiki/` as the bounded skill package.
- Keep all skill-specific templates, scripts, tests, and references inside that folder.
- Do not write into the user's global skill directories during Phase 1.

### 2. Command Surface Should Start As One Skill With Modes

The user initially described operations as `project-wiki-init`, `project-wiki-ingest`, `project-wiki-query`, and `project-wiki-lint`. For packaging, one `project-llm-wiki` skill with explicit mode sections is easier to install and inspect first. Later phases can add thin alias skills if repeated usage proves separate triggers are better.

Planning implication:
- `SKILL.md` should document mode triggers:
  - `project-wiki-init`
  - `project-wiki-lint`
  - `project-wiki-query`
  - `project-wiki-ingest`
  - future `project-wiki-promote`
- Phase 1 should document the command surface, not fully implement all modes.

### 3. Deterministic Helper Script Should Exist Early

Init and lint need deterministic behavior. Even before the full behavior exists, Phase 1 should create a Python standard-library script with a help surface and explicit "not implemented yet" behavior for future modes. This proves the no-dependency execution contract and prevents later phases from inventing separate entrypoints.

Planning implication:
- Create `skills/project-llm-wiki/scripts/project_wiki.py`.
- Script should import only Python standard-library modules.
- `--help` should work.
- Future subcommands should be visible but can return clear planned-mode messages until implemented.

### 4. Templates Should Be Separate Assets, Not Embedded Prompt Bulk

Existing vault skill practice supports `SKILL.md` plus optional `assets/`, `scripts/`, and `references/`. Phase 1 should create this package skeleton so future phases can add `.llm-wiki/` templates without bloating the top-level skill file.

Planning implication:
- Create `assets/templates/README.md` explaining future template ownership.
- Create placeholder or contract files only where needed.
- Avoid writing final `.llm-wiki/` templates until Phase 2.

### 5. Baseline Tests Should Guard Package Shape

Phase 1 can already test:
- Expected package directories exist.
- `SKILL.md` documents the Project LLM Wiki operations.
- Python helper uses no third-party imports.
- `python3 skills/project-llm-wiki/scripts/project_wiki.py --help` exits 0.

Planning implication:
- Add a stdlib test file under `skills/project-llm-wiki/tests/`.
- Add a clear test command to the README and plans.

## Recommended Plan Split

### Plan 01-01: Package Contract and Command Surface

Create human-readable package contract artifacts:
- `README.md`
- `skills/project-llm-wiki/SKILL.md`
- `skills/project-llm-wiki/references/command-surface.md`
- `skills/project-llm-wiki/references/package-contract.md`

Covers:
- `SKILL-01`
- `SKILL-03`

### Plan 01-02: Script Skeleton and Baseline Tests

Create executable no-dependency scaffolding:
- `skills/project-llm-wiki/scripts/project_wiki.py`
- `skills/project-llm-wiki/tests/test_project_wiki_package.py`
- `skills/project-llm-wiki/assets/templates/README.md`
- optional `skills/project-llm-wiki/references/testing.md`

Covers:
- `SKILL-02`
- reinforces `SKILL-03`

## Validation Architecture

Phase 1 validation should use Python standard-library tests because the project intentionally avoids third-party dependencies in the foundation phase.

### Test Infrastructure

| Property | Value |
|----------|-------|
| Framework | Python `unittest` via stdlib |
| Config file | none |
| Quick run command | `python3 -m unittest discover -s skills/project-llm-wiki/tests` |
| Full suite command | `python3 -m unittest discover -s skills/project-llm-wiki/tests` |
| Estimated runtime | under 5 seconds |

### Required Test Coverage

- Package shape exists at `skills/project-llm-wiki/`.
- `SKILL.md` contains `project-wiki-init`, `project-wiki-lint`, `project-wiki-query`, and `project-wiki-ingest`.
- Helper script `--help` exits 0.
- Helper script source does not import non-stdlib project dependencies.
- Reference docs name repo-local `.llm-wiki/` as durable knowledge and `.planning/` as volatile workflow state.

## Risks To Carry Into Planning

- Do not install or mutate global skill directories in Phase 1.
- Do not implement `.llm-wiki/` init behavior before templates are designed in Phase 2.
- Do not split into many skills before the single-package contract is validated.
- Do not introduce dependencies that contradict SKILL-02.

## RESEARCH COMPLETE

Phase 1 has enough context to plan two executable, bounded plans.
