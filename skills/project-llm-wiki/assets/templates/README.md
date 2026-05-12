# Project LLM Wiki Templates

## Phase 1 Status

Final .llm-wiki/ templates are implemented in Phase 2.

This directory exists in Phase 1 so the package has a stable asset location before template content is designed and tested.

## Phase 2 Ownership

Phase 2 owns the final `.llm-wiki/` skeleton templates, idempotent init behavior, and raw source policy files.

Template changes must stay inside the Project LLM Wiki package boundary unless a later plan explicitly adds target repository initialization behavior.

## Template Safety Rules

Templates must not contain secrets, customer data, logs, database exports, or generated dumps.

Templates must preserve the rule that current repo code wins over wiki notes.

Templates must keep durable project knowledge separate from `.planning/`, Linear, OMX, workflow files, pull requests, and other volatile task state.
