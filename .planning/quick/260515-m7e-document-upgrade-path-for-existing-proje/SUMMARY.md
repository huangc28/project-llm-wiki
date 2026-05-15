---
quick_id: 260515-m7e
slug: document-upgrade-path-for-existing-proje
status: complete
completed: 2026-05-15
files:
  - README.md
---

# Quick Task 260515-m7e Summary

Added README guidance for updating existing repos that already use an older Project LLM Wiki setup.

## Changed

- Added an `Updating Existing Repos` section.
- Documented the safe flow: update the skill package, run from the target repo's actual Git root, dry-run first, review output, then apply.
- Clarified that existing `.llm-wiki/` files are preserved, root `AGENTS.md` is marker-updated by default when safe, and `--no-patch-agents` is the intentional opt-out.

## Verification

- `rg -n "Updating Existing Repos|--dry-run|--no-patch-agents|byte-for-byte" README.md`

