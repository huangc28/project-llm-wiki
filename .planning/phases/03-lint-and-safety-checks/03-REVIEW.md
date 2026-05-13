---
phase: 03-lint-and-safety-checks
reviewed: 2026-05-13T04:09:33Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - skills/project-llm-wiki/scripts/project_wiki.py
  - skills/project-llm-wiki/tests/test_project_wiki_lint.py
  - skills/project-llm-wiki/tests/test_project_wiki_package.py
  - skills/project-llm-wiki/references/command-surface.md
  - skills/project-llm-wiki/references/testing.md
findings:
  critical: 1
  warning: 2
  info: 0
  total: 3
status: issues_found
---

# Phase 03: Code Review Report

**Reviewed:** 2026-05-13T04:09:33Z
**Depth:** standard
**Files Reviewed:** 5
**Status:** issues_found

## Summary

Reviewed the Phase 03 lint implementation, lint tests, and command/testing references. The current test suite passes, but the implementation still has a safety gap in secret detection and two correctness gaps that can either miss unscannable wiki content or falsely block valid wikilinks.

## Critical Issues

### CR-01: BLOCKER - Secret Scan Misses Common Key-Value Secrets

**File:** `skills/project-llm-wiki/scripts/project_wiki.py:454`

**Issue:** The secret scan only checks two patterns: PEM private key headers and credential-bearing URLs. The command contract says lint checks "secret-looking content", and the project durability boundary is explicitly "non-secret knowledge", but a raw `.env` or Markdown page containing common forms such as `OPENAI_API_KEY=sk-...`, `GITHUB_TOKEN=...`, `AWS_SECRET_ACCESS_KEY=...`, or `password = "..."` passes clean because neither `PRIVATE_KEY_PATTERN` nor `CREDENTIAL_URL_PATTERN` matches it. That creates a false sense of safety before committing `.llm-wiki/` content.

**Fix:**

```python
KEY_VALUE_SECRET_PATTERN = re.compile(
    r"(?i)\b(?:password|passwd|pwd|secret|api[_-]?key|access[_-]?key|token|bearer|private[_-]?key)\b"
    r"\s*[:=]\s*['\"]?([^'\"\s#]+)"
)
KNOWN_TOKEN_PATTERN = re.compile(
    r"\b(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16})\b"
)
SECRET_PATTERNS = (
    PRIVATE_KEY_PATTERN,
    CREDENTIAL_URL_PATTERN,
    KEY_VALUE_SECRET_PATTERN,
    KNOWN_TOKEN_PATTERN,
)

# In check_secret_like_content:
if not any(pattern.search(text) for pattern in SECRET_PATTERNS):
    continue
```

Add regression tests for key-value secrets in both Markdown and non-Markdown raw files, with placeholder allowlisting only for obvious redacted values such as `REDACTED`, `example`, or `changeme`.

## Warnings

### WR-01: WARNING - Dotted Markdown Page Names Produce False Broken Wikilinks

**File:** `skills/project-llm-wiki/scripts/project_wiki.py:282`

**Issue:** `normalize_wikilink_target()` treats any suffix as an explicit file extension. For a valid Markdown page such as `.llm-wiki/features/api.v2.md`, `index_link_for_page()` suggests `[[features/api.v2]]`, but normalization returns `features/api.v2` instead of `features/api.v2.md`. The same lint run can then report that suggested link as both a broken wikilink and a missing index entry.

**Fix:**

```python
def normalize_wikilink_target(raw_target: str) -> str:
    target = raw_target.split("|", 1)[0].split("#", 1)[0].strip()
    if not target:
        return ""
    pure_target = pathlib.PurePosixPath(target)
    if pure_target.suffix == ".md":
        return pure_target.as_posix()
    return f"{pure_target.as_posix()}.md"
```

Add a regression test with `.llm-wiki/features/api.v2.md` linked from index as `[[features/api.v2]]`.

### WR-02: WARNING - Unreadable Wiki Directories Are Silently Skipped

**File:** `skills/project-llm-wiki/scripts/project_wiki.py:235`

**Issue:** `collect_wiki_files()` catches `OSError` from `current.iterdir()` and continues without adding any finding. If a subdirectory under `.llm-wiki/` cannot be listed, lint can return clean even though broken links, stale pages, or secret-looking raw files inside that subtree were never scanned. This is a fail-open behavior in a safety check.

**Fix:**

```python
def collect_wiki_files(git_root: pathlib.Path) -> tuple[list[pathlib.Path], list[dict[str, str]]]:
    wiki_root = git_root / WIKI_ROOT
    files: list[pathlib.Path] = []
    findings: list[dict[str, str]] = []
    pending = [wiki_root]

    while pending:
        current = pending.pop()
        try:
            entries = sorted(current.iterdir(), key=lambda path: path.as_posix())
        except OSError:
            findings.append(
                make_finding(
                    "error",
                    "unreadable_wiki_directory",
                    repo_relative_path(current, git_root),
                    "Wiki directory could not be listed during lint.",
                    "Fix permissions or remove the unreadable directory before running project-wiki lint.",
                )
            )
            continue
        # existing traversal...
    return sorted(files, key=lambda path: path.relative_to(git_root).as_posix()), findings
```

Thread the collection findings into `run_lint()` before rendering results, and add a regression test that makes a nested `.llm-wiki/raw/...` directory unreadable.

---

_Reviewed: 2026-05-13T04:09:33Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
