---
name: project-wiki-init
description: Initialize a repo-local .llm-wiki/ in the current Git repository using Project LLM Wiki.
---

# project-wiki-init

Thin alias for the `project-wiki-init` mode in `project-llm-wiki`.

When invoked:

1. Read the `project-llm-wiki` skill in the same skill root.
2. Follow its repository-boundary and safety rules.
3. Run the init mode from the target repository's actual Git root.
4. Run `project-wiki init` by default so the alias initializes or updates the repo immediately.
5. Run `project-wiki init --dry-run` only when the user asks to preview, dry run, or avoid writes.

Do not initialize `.llm-wiki/` in a multi-repo parent unless that parent is the intended Git repository.
