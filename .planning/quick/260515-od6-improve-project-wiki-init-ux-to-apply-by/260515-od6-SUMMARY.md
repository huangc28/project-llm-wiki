---
quick_id: 260515-od6
slug: improve-project-wiki-init-ux-to-apply-by
status: complete
completed: 2026-05-15
files:
  - README.md
  - skills/project-wiki-init/SKILL.md
  - skills/project-llm-wiki/tests/test_project_wiki_package.py
---

# Quick Task 260515-od6 Summary

Changed `$project-wiki-init` so it applies the safe init/update by default, with dry-run reserved for explicit preview requests.

## Changed

- Updated the alias skill to run `project-wiki init` by default from the target repo's actual Git root.
- Preserved the explicit preview path with `project-wiki init --dry-run` when the user asks to preview, dry run, or avoid writes.
- Revised README existing-repo update guidance so users can run `$project-wiki-init` directly and still have a clear dry-run checklist when they want one.
- Added package tests that lock the apply-by-default alias and README contract.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests -p 'test_project_wiki_package.py'` — 22 tests passed.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/project-llm-wiki/tests` — 145 tests passed.
- `rg -n 'Prefer \`init --dry-run\` before writing|The alias should run \`project-wiki init --dry-run\` first|dry-run first unless' README.md skills/project-wiki-init/SKILL.md` — no matches.
- `git diff --check` — passed.

Implementation commit: `cb7864a`.
