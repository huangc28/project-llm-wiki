---
phase: 05-agent-instructions-and-real-repo-validation
reviewed: 2026-05-15T07:21:38Z
depth: standard
files_reviewed: 6
files_reviewed_list:
  - skills/project-llm-wiki/SKILL.md
  - skills/project-llm-wiki/references/command-surface.md
  - skills/project-llm-wiki/references/testing.md
  - skills/project-llm-wiki/scripts/project_wiki.py
  - skills/project-llm-wiki/tests/test_project_wiki_init.py
  - skills/project-llm-wiki/tests/test_project_wiki_package.py
findings:
  critical: 1
  warning: 1
  info: 0
  total: 2
status: issues_found
---

# Phase 5: Code Review Report

**Reviewed:** 2026-05-15T07:21:38Z
**Depth:** standard
**Files Reviewed:** 6
**Status:** issues_found

## Summary

Reviewed the Phase 5 Project LLM Wiki skill, command contracts, init helper changes, and package/init tests. The targeted init suite and full package suite both pass, but the new root `AGENTS.md` patch path violates the phase's preservation contract for existing agent instructions when files use non-LF newline bytes.

Verification run during review:

- `python3 -B -m unittest discover -s skills/project-llm-wiki/tests -p test_project_wiki_init.py` - 23 tests passed.
- `python3 -B -m unittest discover -s skills/project-llm-wiki/tests` - 141 tests passed.

## Critical Issues

### CR-01: Text-mode AGENTS.md patching can mutate unrelated instructions

**Classification:** BLOCKER

**File:** `skills/project-llm-wiki/scripts/project_wiki.py:830`

**Issue:** `build_agents_patch_plan()` reads root `AGENTS.md` with `read_text()`, then `apply_agents_patch_plan()` rewrites the full file with `write_text()` at line 906. Python text reads normalize platform newlines, so a repository `AGENTS.md` that uses CRLF will be rewritten with LF outside the managed Project LLM Wiki marker span. That breaks the Phase 5 contract that existing NotebookLM, workflow, and unrelated agent instructions are preserved outside the managed span. The same full-file rewrite also makes append mode mutate every existing line just to add the managed section.

**Fix:**

Patch `AGENTS.md` in a byte-preserving way. One acceptable approach is to read bytes, validate UTF-8 only for marker parsing, preserve existing bytes outside the marker span, and write via an atomic replace.

```python
def read_agents_bytes(agents_path: pathlib.Path) -> tuple[bytes | None, str | None]:
    try:
        raw = agents_path.read_bytes()
        raw.decode("utf-8")
        return raw, None
    except (OSError, UnicodeDecodeError):
        return None, "AGENTS.md: expected readable UTF-8, could not patch Project LLM Wiki section"


def apply_agents_patch_plan(git_root: pathlib.Path, plan: dict[str, object]) -> str:
    action = plan["action"]
    if action in {"skipped", "unchanged"}:
        return "Root AGENTS.md: skipped by --no-patch-agents" if action == "skipped" else "Root AGENTS.md: already up to date"
    if action not in {"create", "append", "update"}:
        return "Root AGENTS.md: already up to date"

    agents_path = git_root / ROOT_AGENTS_RELATIVE_PATH
    temp_path = agents_path.with_name(f".{agents_path.name}.tmp")
    temp_path.write_bytes(plan["content_bytes"])
    temp_path.replace(agents_path)
    return "Root AGENTS.md: created" if action == "create" else "Root AGENTS.md: updated"
```

The concrete implementation can choose a different helper shape, but the invariant should be: bytes outside the managed span remain identical before and after init.

## Warnings

### WR-01: Preservation tests only exercise LF fixtures

**Classification:** WARNING

**File:** `skills/project-llm-wiki/tests/test_project_wiki_init.py:147`

**Issue:** The byte-preservation fixture checks marker-bounded updates with LF-only `textwrap.dedent(...).encode("utf-8")` content. It does not cover CRLF, no-final-newline, or append-mode preservation, so the current suite passes while the implementation can still rewrite unrelated bytes in real `AGENTS.md` files.

**Fix:** Add regression cases that write `AGENTS.md` with `write_bytes()` using CRLF and compare all bytes outside the managed section after both append and marker-replacement runs.

```python
original = (
    b"# Agent Instructions\r\n\r\n"
    b"## NotebookLM Second Brain\r\n"
    b"Keep this guidance byte-for-byte.\r\n"
)
agents.write_bytes(original)

result = self.run_helper(repo, "init")
self.assertEqual(0, result.returncode, result.stdout + result.stderr)
updated = agents.read_bytes()
self.assertTrue(updated.startswith(original))
```

---

_Reviewed: 2026-05-15T07:21:38Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
