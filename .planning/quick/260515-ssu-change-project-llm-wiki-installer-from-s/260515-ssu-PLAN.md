---
quick_id: 260515-ssu
slug: change-project-llm-wiki-installer-from-s
status: in_progress
date: 2026-05-15
---

# Quick Task 260515-ssu Plan

Change Project LLM Wiki installer from symlink-based install to copy-based install with temp clone cleanup, ownership marker, safe update/uninstall, docs/tests.

## Tasks

1. Update installer tests for copy semantics.
   - Installed skills are real directories with `SKILL.md` and an ownership marker.
   - Dry-run writes nothing; re-install updates marker-owned dirs; foreign dirs/symlinks conflict or are preserved.
   - Root bootstrap docs tests expect `mktemp -d`, `trap`, and no default persistent share-dir install model.

2. Implement copy-based install behavior.
   - `install.sh` clones to temp by default, cleans with `trap`, and delegates to helper.
   - `project_wiki.py install` copies five skill dirs into the Codex skills target.
   - Marker-owned dirs are safely replaceable/uninstallable; unmarked paths are protected.

3. Update README and references.
   - Primary user story: curl script temporarily clones, copies skills into Codex, then removes temp clone.
   - Updating remains "rerun the curl command"; symlink/share-dir language moves out or is removed.

4. Verify and commit.
   - Run targeted installer/package tests, full package suite, curl-file temp install smoke, and `git diff --check`.
