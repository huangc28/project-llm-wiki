# Phase 6: User-Friendly Installer and Installation Docs - Context

**Gathered:** 2026-05-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 6 makes Project LLM Wiki installable with a user-friendly first-run path. The user-facing install must be simple enough to explain in one screen: run one command, restart Codex, then run `$project-wiki-init` inside a target repo.

This phase installs the reusable Codex skills on a workstation. It does not initialize `.llm-wiki/` inside any target repository except through the already-existing `$project-wiki-init` flow.

</domain>

<decisions>
## Implementation Decisions

### User-Facing Flow
- **D-01:** The README primary install path is exactly `curl -fsSL https://raw.githubusercontent.com/huangc28/project-llm-wiki/main/install.sh | bash`.
- **D-02:** The visible quick start after install is: restart Codex, then run `$project-wiki-init` in a target git repo.
- **D-03:** Advanced clone/manual symlink instructions must move below the primary quick start, not compete with it.

### Implementation Split
- **D-04:** `install.sh` is the thin public bootstrap. It clones or updates the package into a stable user-local directory and delegates to Python.
- **D-05:** `project_wiki.py install` owns deterministic install behavior for the five Codex skill directories.
- **D-06:** Keep install and init separate: `install` writes only to the Codex skill target; `init` writes only to the target git repo.

### Safety and Defaults
- **D-07:** Default install target is `${CODEX_HOME:-~/.codex}/skills`.
- **D-08:** Re-running install must be idempotent.
- **D-09:** Existing real files or directories in the skill target are conflicts. Do not overwrite them.
- **D-10:** `--force` may replace stale symlinks only; it must not clobber real directories.
- **D-11:** `--uninstall` removes only links owned by this package install.

### the agent's Discretion
The executor may choose exact helper function names and output wording. Keep runtime implementation stdlib-only and keep the shell bootstrap small enough to audit quickly.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Contracts
- `.planning/REQUIREMENTS.md` - Defines INSTALL-01 through INSTALL-06 and TEST-08 through TEST-10.
- `.planning/ROADMAP.md` - Defines Phase 6 goal and success criteria.
- `.planning/STATE.md` - Captures Phase 6 decisions and prior package decisions.
- `AGENTS.md` - Defines repo workflow, GSD, and no-new-dependency constraints.

### Current Package
- `README.md` - Current install section still exposes manual symlink instructions and must become user-first.
- `skills/project-llm-wiki/scripts/project_wiki.py` - Existing Python stdlib CLI; add `install` here.
- `skills/project-llm-wiki/tests/test_project_wiki_package.py` - Existing package/docs tests and helper subprocess pattern.
- `skills/project-llm-wiki/references/command-surface.md` - Add install command contract.
- `skills/project-llm-wiki/references/package-contract.md` - Update the old Phase 1 no-global-install boundary.

### Advisor Input
- `.omx/artifacts/claude-we-are-in-the-project-llm-wiki-repo-main-task-make-installat-2026-05-15T11-20-06-138Z.md` - External recommendation to keep core install logic in `project_wiki.py install` and make shell bootstrap thin.

</canonical_refs>

<specifics>
## Specific Ideas

- The user rejected explanations that require understanding clone/symlink/Python internals before seeing the actual install command.
- The README should start with the shortest successful path, then move all fallback/manual paths to advanced troubleshooting.
- `curl | bash` is acceptable as the public interface only because `install.sh` delegates to a testable Python install subcommand.

</specifics>

<deferred>
## Deferred Ideas

- npm, pip, and non-Codex runtime installers are out of scope for Phase 6.
- Claude Code or other runtime installation can be considered after Codex skill installation is proven.

</deferred>

---

*Phase: 06-user-friendly-installer-and-installation-docs*
*Context gathered: 2026-05-15*
