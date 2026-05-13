---
name: project-wiki-lint
description: Lint a repo-local .llm-wiki/ for structure, safety, freshness, and repo/wiki drift.
---

# project-wiki-lint

Thin alias for the `project-wiki-lint` mode in `project-llm-wiki`.

When invoked:

1. Read the `project-llm-wiki` skill in the same skill root.
2. Follow its lint mode and safety boundaries.
3. Run lint from the target repository's actual Git root.
4. Report errors before warnings, and keep lint read-only.

Use JSON output only when the user asks for parseable output or automation.
