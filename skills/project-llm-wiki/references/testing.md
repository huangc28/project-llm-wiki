# Testing

## Test Command

Run package tests with:

`python3 -m unittest discover -s skills/project-llm-wiki/tests`

## Phase 1 Assertions

Phase 1 tests verify that:

- The skill file documents the project wiki mode names.
- The package contract states the local-only Phase 1 boundary.
- The README points to `skills/project-llm-wiki/SKILL.md`.
- The helper script exposes help, version, and planned-mode behavior.
- Template placeholders defer final `.llm-wiki/` templates to Phase 2.

## No Dependency Rule

The helper script may import argparse, pathlib, sys, and textwrap only in Phase 1.

Tests should use Python standard-library modules only.
