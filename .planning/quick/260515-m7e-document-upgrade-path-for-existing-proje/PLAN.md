---
quick_id: 260515-m7e
slug: document-upgrade-path-for-existing-proje
status: complete
created: 2026-05-15
---

# Quick Task 260515-m7e: Document Upgrade Path for Existing Project LLM Wiki Users

## Goal

Add README guidance for projects that already use an older Project LLM Wiki setup and need to update safely to the current version.

## Tasks

1. Add an `Updating Existing Repos` section to README.
2. Explain the dry-run-first update path and direct CLI fallback.
3. Capture idempotency and root `AGENTS.md` marker-preservation behavior.

## Verification

- `rg -n "Updating Existing Repos|--dry-run|--no-patch-agents|byte-for-byte" README.md`

